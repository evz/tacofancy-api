from flask import Flask, make_response, request, render_template
from flask_sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TACO_CONN']
db = SQLAlchemy(app)

class BaseLayer(db.Model):
    __tablename__ = 'base_layer'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<BaseLayer %r>' % self.name

class Condiment(db.Model):
    __tablename__ = 'condiment'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Condiment %r>' % self.name

class Mixin(db.Model):
    __tablename__ = 'mixin'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Mixin %r>' % self.name

class Seasoning(db.Model):
    __tablename__ = 'seasoning'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Seasoning %r>' % self.name

class Shell(db.Model):
    __tablename__ = 'shell'
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    recipe = db.Column(db.Text)

    def __repr__(self):
        return '<Shell %r>' % self.name

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
