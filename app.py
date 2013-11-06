from flask import Flask, make_response, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
import os
import random
import requests
from os import path
from urlparse import urlparse
from bs4 import BeautifulSoup
import markdown2 as md

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

base_url = 'https://raw.github.com/sinker/tacofancy/master'

class BaseLayer(db.Model):
    __tablename__ = 'base_layer'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<BaseLayer %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Condiment(db.Model):
    __tablename__ = 'condiment'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Condiment %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Mixin(db.Model):
    __tablename__ = 'mixin'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Mixin %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Seasoning(db.Model):
    __tablename__ = 'seasoning'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Seasoning %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Shell(db.Model):
    __tablename__ = 'shell'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Shell %r>' % self.name
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FullTaco(db.Model):
    __tablename__ = 'full_taco'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
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

def get_cookin(model, links):
    saved = []
    for link in links:
        full_url = '%s/%s' % (base_url, link)
        recipe = requests.get(full_url)
        soup = BeautifulSoup(md.markdown(recipe.content))
        name = soup.find('h1')
        if name:
            name = name.text
        else:
            name = ' '.join(path.basename(urlparse(full_url).path).split('_')).title()
        ingredient = db.session.query(model).get(full_url)
        ingredient_data = {
            'url': full_url,
            'name': name,
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
    return saved

MAPPER = {
    'base_layers': BaseLayer,
    'condiments': Condiment, 
    'mixins': Mixin,
    'seasonings': Seasoning,
}

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
            setattr(full_taco, ingredient.__tablename__, ingredient)
            db.session.add(full_taco)
            db.session.commit()
    return None

def fetch_random(model):
    count = model.query.count()
    if count:
        index = random.randint(0, count - 1)
        pk = db.session.query(db.distinct(model.url)).all()[index][0]
        return model.query.get(pk)
    else:
        return None

@app.route('/random/', methods=['GET', 'POST'])
def random_taco():
    condiments = request.args.get('condiments')
    seasonings = request.args.get('seasonings')
    full_taco = request.args.get('full-taco')
    taco = {}
    if full_taco:
        taco = fetch_random(FullTaco).as_dict()
        if taco.get('condiment_url'):
            taco['condiment'] = Condiment.query.get(taco['condiment_url']).as_dict()
        if taco.get('seasoning_url'):
            taco['seasoning'] = Seasoning.query.get(taco['seasoning_url']).as_dict()
        if taco.get('base_layer_url'):
            taco['base_layer'] = BaseLayer.query.get(taco['base_layer_url']).as_dict()
        if taco.get('mixin_url'):
            taco['mixin'] = Mixin.query.get(taco['mixin_url']).as_dict()
        if taco.get('shell_url'):
            taco['shell'] = Shell.query.get(taco['shell_url']).as_dict()
    else:
        if seasonings:
            taco['seasoning'] = fetch_random(Seasoning).as_dict()
        if condiments:
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

@app.route('/cook/')
def cook():
    db.create_all()
    preheat()
    return make_response('did it')

if __name__ == "__main__":
    app.run(debug=True)
