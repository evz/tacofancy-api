from .db import db


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

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

