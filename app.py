from flask import Flask, make_response, request, render_template, current_app, redirect, url_for
from functools import update_wrapper
from flask_sqlalchemy import SQLAlchemy
import json
import os
import random
import requests
from os import path
from urlparse import urlparse
from bs4 import BeautifulSoup
import markdown2 as md
from datetime import timedelta
from slughifi import slughifi

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

##################
##  Data Models ##
##################

class BaseLayer(db.Model):
    __tablename__ = 'base_layer'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<BaseLayer %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Condiment(db.Model):
    __tablename__ = 'condiment'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Condiment %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Mixin(db.Model):
    __tablename__ = 'mixin'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Mixin %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Seasoning(db.Model):
    __tablename__ = 'seasoning'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Seasoning %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Shell(db.Model):
    __tablename__ = 'shell'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Shell %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FullTaco(db.Model):
    __tablename__ = 'full_taco'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    recipe = db.Column(db.Text)
    base_layer_url = db.Column(db.String, db.ForeignKey('base_layer.url'))
    base_layer = db.relationship('BaseLayer', backref=db.backref('full_taco', lazy='dynamic'))
    condiment_url = db.Column(db.String, db.ForeignKey('condiment.url'))
    condiment = db.relationship('Condiment', backref=db.backref('full_taco', lazy='dynamic'))
    mixin_url = db.Column(db.String, db.ForeignKey('mixin.url'))
    mixin = db.relationship('Mixin', backref=db.backref('full_taco', lazy='dynamic'))
    seasoning_url = db.Column(db.String, db.ForeignKey('seasoning.url'))
    seasoning = db.relationship('Seasoning', backref=db.backref('full_taco', lazy='dynamic'))
    shell_url = db.Column(db.String, db.ForeignKey('shell.url'))
    shell = db.relationship('Shell', backref=db.backref('full_taco', lazy='dynamic'))

    def __repr__(self):
        return '<FullTaco %r>' % self.name 
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

contrib_fulltaco = db.Table(
    'contrib_fulltaco',
    db.Column('contrib_username', db.String, db.ForeignKey('contributor.username')),
    db.Column('full_taco_url', db.String, db.ForeignKey('full_taco.url')),
)
contrib_shell = db.Table(
    'contrib_shell',
    db.Column('contrib_username', db.String, db.ForeignKey('contributor.username')),
    db.Column('shell_url', db.String, db.ForeignKey('shell.url')),
)
contrib_seasoning = db.Table(
    'contrib_seasoning',
    db.Column('contrib_username', db.String, db.ForeignKey('contributor.username')),
    db.Column('seasoning_url', db.String, db.ForeignKey('seasoning.url')),
)
contrib_mixin = db.Table(
    'contrib_mixin',
    db.Column('contrib_username', db.String, db.ForeignKey('contributor.username')),
    db.Column('mixin_url', db.String, db.ForeignKey('mixin.url')),
)
contrib_condiment = db.Table(
    'contrib_condiment',
    db.Column('contrib_username', db.String, db.ForeignKey('contributor.username')),
    db.Column('condiment_url', db.String, db.ForeignKey('condiment.url')),
)
contrib_baselayer = db.Table(
    'contrib_baselayer',
    db.Column('contrib_username', db.String, db.ForeignKey('contributor.username')),
    db.Column('baselayer_url', db.String, db.ForeignKey('base_layer.url')),
)

class Contributor(db.Model):
    __tablename__ = 'contributor'
    username = db.Column(db.String, primary_key=True)
    gravatar = db.Column(db.String)
    full_name = db.Column(db.String)
    full_tacos = db.relationship('FullTaco', secondary=contrib_fulltaco,
        backref=db.backref('contributors', lazy='dynamic'))
    shells = db.relationship('Shell', secondary=contrib_shell,
        backref=db.backref('contributors', lazy='dynamic'))
    seasonings = db.relationship('Seasoning', secondary=contrib_seasoning,
        backref=db.backref('contributors', lazy='dynamic'))
    mixins = db.relationship('Mixin', secondary=contrib_mixin,
        backref=db.backref('contributors', lazy='dynamic'))
    condiments = db.relationship('Condiment', secondary=contrib_condiment,
        backref=db.backref('contributors', lazy='dynamic'))
    base_layers = db.relationship('BaseLayer', secondary=contrib_baselayer,
        backref=db.backref('contributors', lazy='dynamic'))
    
    def __repr__(self):
        return '<Contributor %r>' % self.username
    # It seems like it should be possible to call the github commits endpoint
    # loop over the commits to get the user, then call the specific endpoint 
    # for each commit to get the files effected (which would give us the recipe)
    # Should decide on what other data to capture about a user. Maybe just gravatar?


#############################
##  Data loading functions ##
#############################

base_url = 'https://raw.github.com/sinker/tacofancy/master'

MAPPER = {
    'base_layers': BaseLayer,
    'condiments': Condiment, 
    'mixins': Mixin,
    'seasonings': Seasoning,
    'shells': Shell
}

def get_cookin(model, links):
    saved = []
    for link in links:
        full_url = '%s/%s' % (base_url, link)
        recipe = requests.get(full_url)
        if recipe.status_code is 200:
            soup = BeautifulSoup(md.markdown(recipe.content))
            name = soup.find('h1')
            if name:
                name = name.text
            else:
                name = ' '.join(path.basename(urlparse(full_url).path).split('_')).replace('.md', '').title()
            ingredient = db.session.query(model).get(full_url)
            ingredient_data = {
                'url': full_url,
                'name': name,
                'slug': slughifi(name),
                'recipe': recipe.content.decode('utf-8'),
            }
            if not ingredient:
                ingredient = model(**ingredient_data)
                db.session.add(ingredient)
                db.session.commit()
            else:
                for k,v in ingredient_data.items():
                    setattr(ingredient, k, v)
                db.session.add(ingredient)
                db.session.commit()
            saved.append(ingredient)
        else:
            ingredient = model.query.get(full_url)
            if ingredient:
                db.session.delete(ingredient)
                db.session.commit()
    return saved

def preheat():
    index = requests.get('%s/INDEX.md' % base_url)
    soup = BeautifulSoup(md.markdown(index.content))
    links = [a for a in soup.find_all('a') if a.get('href').endswith('.md')]
    full_tacos = [f.get('href') for f in links if 'full_tacos/' in f.get('href')]
    base_layers = [b.get('href') for b in links if 'base_layers/' in b.get('href')]
    mixins = [m.get('href') for m in links if 'mixins/' in m.get('href')]
    condiments = [c.get('href') for c in links if 'condiments/' in c.get('href')]
    seasonings = [s.get('href') for s in links if 'seasonings/' in s.get('href')]
    bases = get_cookin(BaseLayer, base_layers)
    conds = get_cookin(Condiment, condiments)
    seas = get_cookin(Seasoning, seasonings)
    mix = get_cookin(Mixin, mixins)
    for full_taco in get_cookin(FullTaco, full_tacos):
        soup = BeautifulSoup(md.markdown(full_taco.recipe))
        ingredient_links = [l.get('href') for l in soup.find_all('a') if l.get('href').endswith('.md')]
        for link in ingredient_links:
            parts = urlparse(link).path.split('/')[-2:]
            kind = MAPPER[parts[0]]
            scrubbed_link = '/'.join(parts)
            full_link = '%s/%s' % (base_url, scrubbed_link)
            ingredient = db.session.query(kind).get(full_link)
            if ingredient:
                setattr(full_taco, ingredient.__tablename__, ingredient)
                db.session.add(full_taco)
                db.session.commit()
    return None

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

##############################################
##  Cross Domain decorator for Flask routes ##
##############################################

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

###################
##  Flask routes ##
###################

@app.route('/random/', methods=['GET', 'POST'])
@crossdomain(origin="*")
def random_taco():
    full_taco = request.args.get('full-taco')
    taco = {}
    if full_taco:
        taco_obj = fetch_random(FullTaco)
        taco = taco_obj.as_dict()
        if taco.get('condiment_url'):
            taco['condiment'] = taco_obj.condiment.as_dict()
        if taco.get('seasoning_url'):
            taco['seasoning'] = taco_obj.seasoning.as_dict()
        if taco.get('base_layer_url'):
            taco['base_layer'] = taco_obj.base_layer.as_dict()
            taco['base_layer']['slug'] = taco_obj.base_layer.slug
        if taco.get('mixin_url'):
            taco['mixin'] = taco_obj.mixin.as_dict()
        if taco.get('shell_url'):
            taco['shell'] = taco_obj.shell.as_dict()
    else:
        taco['seasoning'] = fetch_random(Seasoning).as_dict()
        taco['condiment'] = fetch_random(Condiment).as_dict()
        taco['mixin'] = fetch_random(Mixin).as_dict()
        taco['base_layer'] = fetch_random(BaseLayer).as_dict()
        
        # Gotta do this junk here cause there's no shells yet. Damn.
        shell = fetch_random(Shell)
        if shell:
            taco['shell'] = shell.as_dict()
    resp = make_response(json.dumps(taco))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>/')
def permalink(path):
    try:
        base_layer, mixin, condiment, seasoning = path.split('/')
    except ValueError:
        return redirect(url_for('index'))
    context = {}
    context['base_layer'] = BaseLayer.query.filter_by(slug=base_layer).first()
    context['mixin'] = Mixin.query.filter_by(slug=mixin).first()
    context['condiment'] = Condiment.query.filter_by(slug=condiment).first()
    context['seasoning'] = Seasoning.query.filter_by(slug=seasoning).first()
    return render_template('permalink.html', **context)

@app.route('/cook/', methods=['GET', 'POST'])
def cook():
    db.create_all()
    preheat()
    return make_response('did it')

if __name__ == "__main__":
    app.run(debug=True)
