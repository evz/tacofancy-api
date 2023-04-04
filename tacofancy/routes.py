import random

from flask import jsonify, Blueprint, request, current_app, redirect, render_template, url_for

from ariadne import graphql_sync

from .graphql import explorer_html, schema
from .models import BaseLayer, Mixin, Condiment, Seasoning, Shell
from .db import db

routes = Blueprint("routes", __name__, template_folder="templates")

########################
##  Stupid randomizer ##
########################

def fetch_random(model):
    count = model.query.count()
    if count:
        index = random.randint(0, count - 1)
        pk = db.session.query(db.distinct(model.url)).all()[index][0]
        return model.query.get(pk)
    else:
        return None

def fetch_random_ingredients():
    taco = {}
    taco['seasoning'] = fetch_random(Seasoning)
    taco['condiment'] = fetch_random(Condiment)
    taco['mixin'] = fetch_random(Mixin)
    taco['base_layer'] = fetch_random(BaseLayer)
    taco['shell'] = fetch_random(Shell)
    return taco

@routes.route('/')
def index():
    taco = fetch_random_ingredients()
    taco['render_link'] = True
    return render_template('permalink.html', **taco)

@routes.route('/<path:path>/')
def permalink(path):
    try:
        base_layer, mixin, condiment, seasoning, shell = path.split('/')
    except ValueError:
        return redirect(url_for('routes.index'))
    taco = {}
    taco['base_layer'] = BaseLayer.query.filter_by(slug=base_layer).first()
    taco['mixin'] = Mixin.query.filter_by(slug=mixin).first()
    taco['condiment'] = Condiment.query.filter_by(slug=condiment).first()
    taco['seasoning'] = Seasoning.query.filter_by(slug=seasoning).first()
    taco['shell'] = Shell.query.filter_by(slug=shell).first()
    taco['render_link'] = False
    return render_template('permalink.html', **taco)

@routes.route("/graphql", methods=["GET"])
def graphql_explorer():
    return explorer_html, 200


@routes.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value={"request": request},
        debug=current_app.debug
    )

    if success:
        status_code = 200
    else:
        status_code = 400
    return jsonify(result), status_code
