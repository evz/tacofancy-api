from app import db, Contributor, BaseLayer, Mixin, Condiment, Seasoning, MAPPER
import os
import pprint
import requests

TOKEN = os.environ['GITHUB_TOKEN']
headers = {'Authorization': 'token %s' % TOKEN}

def get_commits_page(url):
    r = requests.get(url, headers=headers)
    pages = r.headers['Link'].split(',')
    if len(pages) is 2:
        return pages[0].split(';')[0][1:-1], r.json()
    else:
        return None, r.json()

def get_all_commits(url, all_commits=[]):
    r = requests.get(url, headers=headers)
    yield r.json()
    pages = r.headers['Link'].split(',')
    if len(pages) is 2:
        all_commits = []
        url = pages[0].split(';')[0][1:-1]
        while True:
            next_page, resp = get_commits_page(url)
            yield resp
            if next_page:
                url = next_page
                continue
            else:
                break

def add_contributor(data, contributions):
    contributor = db.session.query(Contributor).filter_by(username=data['username']).first()
    if not contributor:
        contributor = Contributor(**data)
        db.session.add(contributor)
        db.session.commit()
    for contribution in contributions:
        ing_type = contribution.split('/')[-2]
        if ing_type in MAPPER.keys():
            model = MAPPER[ing_type]
            ingredient = db.session.query(model).get(contribution)
            if not ingredient:
                # Might be an opportunity here to make the missing ingredients
                continue
            if getattr(contributor, ing_type):
                stored = getattr(contributor, ing_type)
                stored.append(ingredient)
                setattr(contributor, ing_type, stored)
            else:
                setattr(contributor, ing_type, [ingredient])
            db.session.add(contributor)
            db.session.commit()

if __name__ == '__main__':
    import sys
    repo_name = sys.argv[1]
    commits_url = 'https://api.github.com/repos/%s/commits' % repo_name
    all_commits = []
    for page in get_all_commits(commits_url):
        all_commits.extend(page)
    raw_base = 'https://raw.github.com/%s/master/' % repo_name
    ignore_these = ['LICENSE', '.gitignore', '.DS_Store', 'INDEX.md', 'README.md']
    for commit in all_commits:
        commit_detail = requests.get(commit['url'], headers=headers)
        commit_data = commit_detail.json()
        data = {}
        if commit_data.get('author'):
            data['username'] = commit_data['author']['login']
            data['gravatar'] = commit_data['author']['avatar_url']
        else:
            data['username'] = commit_data['commit']['author']['name']
        data['full_name'] = commit_data['commit']['author']['name']
        files = []
        for f in commit_data['files']:
            base = f['filename'].split('/')[-1]
            if base not in ignore_these:
                files.append('%s%s' % (raw_base, f['filename']))
        add_contributor(data, files)
