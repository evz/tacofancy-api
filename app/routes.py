from flask import Blueprint, render_template, redirect, url_for
from .models import db, BaseLayer, Condiment, Mixin, Seasoning, Shell
from .utils import fetch_random_ingredients

# Create blueprint for template routes
template_routes = Blueprint('templates', __name__)


@template_routes.route('/')
def index():
    """Home page with a random taco."""
    taco = fetch_random_ingredients(db.session)
    taco['render_link'] = True
    return render_template('permalink.html', **taco)


@template_routes.route('/<path:path>/')
def permalink(path: str):
    """Permalink to a specific taco combination."""
    try:
        base_layer, mixin, condiment, seasoning, shell = path.split('/')
    except ValueError:
        return redirect(url_for('templates.index'))
    
    taco = {
        'base_layer': BaseLayer.query.filter_by(slug=base_layer).first(),
        'mixin': Mixin.query.filter_by(slug=mixin).first(),
        'condiment': Condiment.query.filter_by(slug=condiment).first(),
        'seasoning': Seasoning.query.filter_by(slug=seasoning).first(),
        'shell': Shell.query.filter_by(slug=shell).first(),
        'render_link': False
    }
    return render_template('permalink.html', **taco)