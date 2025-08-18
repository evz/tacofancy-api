from flask import request
from flask_restful import Api, Resource
from .models import db, BaseLayer, Condiment, Mixin, Seasoning, Shell, FullTaco, Contributor, MAPPER
from .utils import fetch_random_ingredients, fetch_random


class RecipeListResource(Resource):
    """Generic resource for recipe collections."""
    
    def __init__(self, recipe_type):
        self.recipe_type = recipe_type
        self.model = MAPPER[recipe_type]
    
    def get(self):
        """Get all items for this recipe type."""
        items = self.model.query.all()
        return [item.as_dict() for item in items]


class RecipeResource(Resource):
    """Generic resource for individual recipes."""
    
    def __init__(self, recipe_type):
        self.recipe_type = recipe_type
        self.model = MAPPER[recipe_type]
    
    def get(self, slug):
        """Get a single item by slug."""
        item = self.model.query.filter_by(slug=slug).first()
        if not item:
            return {
                'status': 'error', 
                'message': f'{self.recipe_type} with the slug "{slug}" not found'
            }, 404
        return item.as_dict()


class RandomTacoResource(Resource):
    """Resource for random taco generation."""
    
    def get(self):
        """Get a random taco or random ingredients."""
        full_taco = request.args.get('full-taco')
        
        if full_taco:
            taco_obj = fetch_random(FullTaco, db.session)
            if not taco_obj:
                return {'error': 'No full tacos available'}, 404
                
            taco = taco_obj.as_dict()
            
            # Include related objects
            if taco.get('condiment_url') and taco_obj.condiment:
                taco['condiment'] = taco_obj.condiment.as_dict()
            if taco.get('seasoning_url') and taco_obj.seasoning:
                taco['seasoning'] = taco_obj.seasoning.as_dict()
            if taco.get('base_layer_url') and taco_obj.base_layer:
                taco['base_layer'] = taco_obj.base_layer.as_dict()
            if taco.get('mixin_url') and taco_obj.mixin:
                taco['mixin'] = taco_obj.mixin.as_dict()
            if taco.get('shell_url') and taco_obj.shell:
                taco['shell'] = taco_obj.shell.as_dict()
                
            return taco
        else:
            # Random ingredients
            data = fetch_random_ingredients(db.session)
            taco = {}
            for k, v in data.items():
                if v:
                    taco[k] = v.as_dict()
            return taco


class ContributorListResource(Resource):
    """Resource for contributor listings."""
    
    def get(self):
        """Get all contributors."""
        contributors = Contributor.query.all()
        return [c.as_dict() for c in contributors]


class ContributorResource(Resource):
    """Resource for individual contributors."""
    
    def get(self, username):
        """Get contributions for a specific user."""
        contributor = Contributor.query.filter_by(username=username).first()
        if not contributor:
            return {'error': f'Contributor with github username "{username}" not found'}, 404
        
        data = contributor.as_dict()
        data['base_layers'] = [b.name for b in contributor.base_layers]
        data['condiments'] = [c.name for c in contributor.condiments]
        data['mixins'] = [m.name for m in contributor.mixins]
        data['shells'] = [s.name for s in contributor.shells]
        data['seasonings'] = [s.name for s in contributor.seasonings]
        
        return data


class RecipeSlugsResource(Resource):
    """Resource for recipe slug listings."""
    
    def get(self, layer_type):
        """Get all recipe slugs for a given layer type."""
        if layer_type not in MAPPER:
            return {'error': f'Invalid layer type: {layer_type}'}, 404
        
        model = MAPPER[layer_type]
        slugs = [{'name': item.name, 'slug': item.slug} for item in model.query.all()]
        return slugs


class RecipeContributorsResource(Resource):
    """Resource for recipe contributors."""
    
    def get(self, recipe_type, recipe_slug):
        """Get contributors for a specific recipe."""
        if recipe_type not in MAPPER:
            return {'error': f'Invalid recipe type: {recipe_type}'}, 404
        
        model = MAPPER[recipe_type]
        recipe = model.query.filter_by(slug=recipe_slug).first()
        if not recipe:
            return {'error': f'Recipe not found: {recipe_type}/{recipe_slug}'}, 404
        
        return [c.as_dict() for c in recipe.contributors]


# Create specific resource classes for each recipe type
class BaseLayersListResource(RecipeListResource):
    def __init__(self):
        super().__init__('base_layers')

class BaseLayersResource(RecipeResource):
    def __init__(self):
        super().__init__('base_layers')

class CondimentsListResource(RecipeListResource):
    def __init__(self):
        super().__init__('condiments')

class CondimentsResource(RecipeResource):
    def __init__(self):
        super().__init__('condiments')

class MixinsListResource(RecipeListResource):
    def __init__(self):
        super().__init__('mixins')

class MixinsResource(RecipeResource):
    def __init__(self):
        super().__init__('mixins')

class SeasoningsListResource(RecipeListResource):
    def __init__(self):
        super().__init__('seasonings')

class SeasoningsResource(RecipeResource):
    def __init__(self):
        super().__init__('seasonings')

class ShellsListResource(RecipeListResource):
    def __init__(self):
        super().__init__('shells')

class ShellsResource(RecipeResource):
    def __init__(self):
        super().__init__('shells')


def setup_api(app):
    """Setup Flask-RESTful API with all routes."""
    api = Api(app)
    
    # Random taco endpoint
    api.add_resource(RandomTacoResource, '/random/')
    
    # Recipe endpoints
    api.add_resource(BaseLayersListResource, '/base_layers/')
    api.add_resource(BaseLayersResource, '/base_layers/<slug>/')
    
    api.add_resource(CondimentsListResource, '/condiments/')
    api.add_resource(CondimentsResource, '/condiments/<slug>/')
    
    api.add_resource(MixinsListResource, '/mixins/')
    api.add_resource(MixinsResource, '/mixins/<slug>/')
    
    api.add_resource(SeasoningsListResource, '/seasonings/')
    api.add_resource(SeasoningsResource, '/seasonings/<slug>/')
    
    api.add_resource(ShellsListResource, '/shells/')
    api.add_resource(ShellsResource, '/shells/<slug>/')
    
    # Contributor endpoints
    api.add_resource(ContributorListResource, '/contributions/')
    api.add_resource(ContributorResource, '/contributions/<username>/')
    
    # Recipe metadata endpoints
    api.add_resource(RecipeSlugsResource, '/contributors/<layer_type>/')
    api.add_resource(RecipeContributorsResource, '/contributors/<recipe_type>/<recipe_slug>/')
    
    return api