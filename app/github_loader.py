import os
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
from github import Github, GithubException
from bs4 import BeautifulSoup
import markdown2 as md
from .models import db, BaseLayer, Condiment, Mixin, Seasoning, Shell, FullTaco, Contributor, SyncMetadata, MAPPER
from .utils import slugify

logger = logging.getLogger(__name__)

REPO_OWNER = "dansinker"
REPO_NAME = "tacofancy"
BRANCH = "master"


class TacoFancyLoader:
    def __init__(self, github_token: Optional[str] = None):
        """Initialize the loader with optional GitHub token for rate limiting."""
        if github_token:
            self.github = Github(github_token)
        else:
            self.github = Github()  # Anonymous access (lower rate limits)
        
        self.repo = self.github.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    def get_last_sync_sha(self, sync_type: str) -> Optional[str]:
        """Get the last processed commit SHA for a given sync type."""
        sync_record = db.session.query(SyncMetadata).filter_by(sync_type=sync_type).first()
        return sync_record.last_commit_sha if sync_record else None
    
    def update_sync_metadata(self, sync_type: str, commit_sha: str):
        """Update the sync metadata with the latest processed commit SHA."""
        sync_record = db.session.query(SyncMetadata).filter_by(sync_type=sync_type).first()
        if sync_record:
            sync_record.last_commit_sha = commit_sha
            sync_record.last_sync_time = db.func.now()
        else:
            sync_record = SyncMetadata(
                sync_type=sync_type,
                last_commit_sha=commit_sha
            )
            db.session.add(sync_record)
        db.session.commit()
    
    def get_recipe_files_by_category(self) -> Dict[str, List[str]]:
        """Get all recipe files organized by category."""
        try:
            # Get the repository tree
            tree = self.repo.get_git_tree(BRANCH, recursive=True)
            
            categories = {
                'base_layers': [],
                'condiments': [],
                'mixins': [],
                'seasonings': [],
                'shells': [],
                'full_tacos': []
            }
            
            for item in tree.tree:
                if item.type == "blob" and item.path.endswith('.md'):
                    # Skip index and readme files
                    if item.path.lower() in ['index.md', 'readme.md']:
                        continue
                    
                    # Categorize by directory
                    path_parts = item.path.split('/')
                    if len(path_parts) >= 2:
                        category = path_parts[0]
                        if category in categories:
                            categories[category].append(item.path)
            
            return categories
            
        except GithubException as e:
            logger.error(f"Error fetching repository tree: {e}")
            raise
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get the content of a specific file."""
        try:
            file_content = self.repo.get_contents(file_path, ref=BRANCH)
            return file_content.decoded_content.decode('utf-8')
        except GithubException as e:
            logger.warning(f"Could not fetch {file_path}: {e}")
            return None
    
    def extract_recipe_data(self, content: str, file_path: str) -> Dict[str, str]:
        """Extract recipe data from markdown content."""
        # Convert markdown to HTML and parse
        html = md.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to get name from first H1, otherwise derive from filename
        name_element = soup.find('h1')
        if name_element:
            name = name_element.get_text().strip()
        else:
            # Derive name from filename
            filename = os.path.basename(file_path)
            name = filename.replace('.md', '').replace('_', ' ').title()
        
        return {
            'name': name,
            'slug': slugify(name),
            'recipe': content,
            'url': f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{file_path}"
        }
    
    def load_recipes_for_category(self, category: str, model_class) -> List:
        """Load all recipes for a specific category."""
        categories = self.get_recipe_files_by_category()
        files = categories.get(category, [])
        
        saved_recipes = []
        
        for file_path in files:
            content = self.get_file_content(file_path)
            if content:
                recipe_data = self.extract_recipe_data(content, file_path)
                
                # Check if recipe already exists
                existing = db.session.get(model_class, recipe_data['url'])
                
                if existing:
                    # Update existing recipe
                    for key, value in recipe_data.items():
                        setattr(existing, key, value)
                    saved_recipes.append(existing)
                else:
                    # Create new recipe
                    recipe = model_class(**recipe_data)
                    db.session.add(recipe)
                    saved_recipes.append(recipe)
        
        db.session.commit()
        return saved_recipes
    
    def load_all_recipes(self):
        """Load all recipes from the TacoFancy repository."""
        logger.info("Starting to load recipes from GitHub...")
        
        # Load individual ingredients
        self.load_recipes_for_category('base_layers', BaseLayer)
        logger.info("Loaded base layers")
        
        self.load_recipes_for_category('condiments', Condiment)
        logger.info("Loaded condiments")
        
        self.load_recipes_for_category('seasonings', Seasoning)
        logger.info("Loaded seasonings")
        
        self.load_recipes_for_category('mixins', Mixin)
        logger.info("Loaded mixins")
        
        self.load_recipes_for_category('shells', Shell)
        logger.info("Loaded shells")
        
        # Load full tacos and link them to ingredients
        full_tacos = self.load_recipes_for_category('full_tacos', FullTaco)
        logger.info(f"Loaded {len(full_tacos)} full tacos")
        
        # Link full tacos to their ingredients
        self._link_full_tacos_to_ingredients(full_tacos)
        
        logger.info("Finished loading all recipes")
    
    def _link_full_tacos_to_ingredients(self, full_tacos: List[FullTaco]):
        """Link full tacos to their ingredient components."""
        for full_taco in full_tacos:
            if not full_taco.recipe:
                continue
                
            # Parse the recipe content for ingredient links
            html = md.markdown(full_taco.recipe)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all markdown links that point to recipe files
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                if href.endswith('.md'):
                    # Extract category and construct full URL
                    path_parts = urlparse(href).path.strip('/').split('/')
                    if len(path_parts) >= 2:
                        category = path_parts[-2]  # e.g., 'base_layers'
                        
                        if category in MAPPER:
                            model_class = MAPPER[category]
                            ingredient_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{href}"
                            
                            # Find the ingredient in the database
                            ingredient = db.session.get(model_class, ingredient_url)
                            if ingredient:
                                # Link the ingredient to the full taco
                                column_name = ingredient.__tablename__
                                if hasattr(full_taco, column_name):
                                    setattr(full_taco, column_name, ingredient)
        
        db.session.commit()
    
    def load_contributors(self, incremental: bool = True):
        """Load contributor data efficiently by analyzing commits with file info."""
        logger.info("Loading contributors from commit history...")
        
        try:
            # Check for last processed commit if doing incremental update
            last_sha = None
            if incremental:
                last_sha = self.get_last_sync_sha('contributors')
                if last_sha:
                    logger.info(f"Resuming from last processed commit: {last_sha}")
            
            # Get commits with file information - this is much more efficient
            # than getting detailed commit info for each commit separately
            commits = self.repo.get_commits()
            
            contributors_seen = set()
            processed_count = 0
            latest_commit_sha = None
            
            for commit in commits:
                try:
                    # Stop if we've reached the last processed commit
                    if last_sha and commit.sha == last_sha:
                        logger.info(f"Reached last processed commit {last_sha}, stopping")
                        break
                    
                    # Store the first (latest) commit SHA for updating sync metadata
                    if latest_commit_sha is None:
                        latest_commit_sha = commit.sha
                    
                    # Extract contributor info from the commit object
                    contributor_data = self._extract_contributor_from_commit(commit)
                    if not contributor_data:
                        continue
                    
                    username = contributor_data['username']
                    
                    # Find or create contributor (only once per username)
                    if username not in contributors_seen:
                        contributor = db.session.get(Contributor, username)
                        if not contributor:
                            contributor = Contributor(**contributor_data)
                            db.session.add(contributor)
                            db.session.flush()  # Get the object in session without committing
                        contributors_seen.add(username)
                    else:
                        contributor = db.session.get(Contributor, username)
                    
                    # Process files modified in this commit
                    self._process_commit_files(contributor, commit)
                    processed_count += 1
                    
                    # Commit periodically to avoid large transactions
                    if processed_count % 50 == 0:
                        db.session.commit()
                        logger.info(f"Processed {processed_count} commits...")
                
                except Exception as e:
                    logger.warning(f"Error processing commit {commit.sha}: {e}")
                    continue
            
            db.session.commit()
            
            # Update sync metadata with the latest commit SHA
            if latest_commit_sha and processed_count > 0:
                self.update_sync_metadata('contributors', latest_commit_sha)
                logger.info(f"Updated sync metadata with latest commit: {latest_commit_sha}")
            
            logger.info(f"Finished processing {processed_count} commits, found {len(contributors_seen)} contributors")
            
        except GithubException as e:
            logger.error(f"Error loading contributors: {e}")
            raise
    
    def _extract_contributor_from_commit(self, commit) -> Optional[Dict[str, str]]:
        """Extract contributor data from a commit object."""
        try:
            if commit.author:
                return {
                    'username': commit.author.login,
                    'gravatar': commit.author.avatar_url,
                    'full_name': commit.commit.author.name or commit.author.login
                }
            elif commit.commit.author:
                # Fallback for commits without GitHub user association
                return {
                    'username': commit.commit.author.name,
                    'gravatar': None,
                    'full_name': commit.commit.author.name
                }
        except AttributeError:
            pass
        
        return None
    
    def _process_commit_files(self, contributor: Contributor, commit):
        """Process files in a commit and link to contributor."""
        try:
            # Access files from the commit - this doesn't require additional API calls
            for file in commit.files:
                if not file.filename.endswith('.md'):
                    continue
                
                # Skip non-recipe files
                filename = os.path.basename(file.filename)
                if filename.lower() in ['index.md', 'readme.md', 'license']:
                    continue
                
                # Determine recipe category from file path
                path_parts = file.filename.split('/')
                if len(path_parts) >= 2:
                    category = path_parts[0]
                    
                    if category in MAPPER:
                        model_class = MAPPER[category]
                        recipe_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{file.filename}"
                        
                        # Find the recipe in the database
                        recipe = db.session.get(model_class, recipe_url)
                        if recipe and recipe not in getattr(contributor, category, []):
                            # Add recipe to contributor's collection
                            if hasattr(contributor, category):
                                getattr(contributor, category).append(recipe)
        
        except Exception as e:
            logger.warning(f"Error processing files for contributor {contributor.username}: {e}")
    
    def load_all_data(self, incremental: bool = True):
        """Load all recipes and contributor data."""
        self.load_all_recipes()
        self.load_contributors(incremental=incremental)


def load_tacofancy_data(github_token: Optional[str] = None, include_contributors: bool = True, incremental: bool = True):
    """Convenience function to load all TacoFancy data."""
    loader = TacoFancyLoader(github_token)
    if include_contributors:
        loader.load_all_data(incremental=incremental)
    else:
        loader.load_all_recipes()