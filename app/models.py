from typing import List, Optional
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime


# Create the SQLAlchemy instance
db = SQLAlchemy()


# Association tables for many-to-many relationships
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


class BaseLayer(db.Model):
    __tablename__ = 'base_layer'
    
    url: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    slug: Mapped[Optional[str]] = mapped_column(String)
    recipe: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    contributors: Mapped[List["Contributor"]] = relationship(
        secondary=contrib_baselayer, back_populates="base_layers"
    )

    def __repr__(self) -> str:
        return f'<BaseLayer {self.name!r}>'
    
    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Condiment(db.Model):
    __tablename__ = 'condiment'
    
    url: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    slug: Mapped[Optional[str]] = mapped_column(String)
    recipe: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    contributors: Mapped[List["Contributor"]] = relationship(
        secondary=contrib_condiment, back_populates="condiments"
    )

    def __repr__(self) -> str:
        return f'<Condiment {self.name!r}>'
    
    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Mixin(db.Model):
    __tablename__ = 'mixin'
    
    url: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    slug: Mapped[Optional[str]] = mapped_column(String)
    recipe: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    contributors: Mapped[List["Contributor"]] = relationship(
        secondary=contrib_mixin, back_populates="mixins"
    )

    def __repr__(self) -> str:
        return f'<Mixin {self.name!r}>'
    
    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Seasoning(db.Model):
    __tablename__ = 'seasoning'
    
    url: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    slug: Mapped[Optional[str]] = mapped_column(String)
    recipe: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    contributors: Mapped[List["Contributor"]] = relationship(
        secondary=contrib_seasoning, back_populates="seasonings"
    )

    def __repr__(self) -> str:
        return f'<Seasoning {self.name!r}>'
    
    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Shell(db.Model):
    __tablename__ = 'shell'
    
    url: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    slug: Mapped[Optional[str]] = mapped_column(String)
    recipe: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    contributors: Mapped[List["Contributor"]] = relationship(
        secondary=contrib_shell, back_populates="shells"
    )

    def __repr__(self) -> str:
        return f'<Shell {self.name!r}>'
    
    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FullTaco(db.Model):
    __tablename__ = 'full_taco'
    
    url: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    slug: Mapped[Optional[str]] = mapped_column(String)
    recipe: Mapped[Optional[str]] = mapped_column(Text)
    
    # Foreign keys
    base_layer_url: Mapped[Optional[str]] = mapped_column(ForeignKey('base_layer.url'))
    condiment_url: Mapped[Optional[str]] = mapped_column(ForeignKey('condiment.url'))
    mixin_url: Mapped[Optional[str]] = mapped_column(ForeignKey('mixin.url'))
    seasoning_url: Mapped[Optional[str]] = mapped_column(ForeignKey('seasoning.url'))
    shell_url: Mapped[Optional[str]] = mapped_column(ForeignKey('shell.url'))
    
    # Relationships
    base_layer: Mapped[Optional["BaseLayer"]] = relationship()
    condiment: Mapped[Optional["Condiment"]] = relationship()
    mixin: Mapped[Optional["Mixin"]] = relationship()
    seasoning: Mapped[Optional["Seasoning"]] = relationship()
    shell: Mapped[Optional["Shell"]] = relationship()
    
    contributors: Mapped[List["Contributor"]] = relationship(
        secondary=contrib_fulltaco, back_populates="full_tacos"
    )

    def __repr__(self) -> str:
        return f'<FullTaco {self.name!r}>' 
    
    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Contributor(db.Model):
    __tablename__ = 'contributor'
    
    username: Mapped[str] = mapped_column(String, primary_key=True)
    gravatar: Mapped[Optional[str]] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    
    # Many-to-many relationships
    full_tacos: Mapped[List[FullTaco]] = relationship(
        secondary=contrib_fulltaco, back_populates="contributors"
    )
    shells: Mapped[List[Shell]] = relationship(
        secondary=contrib_shell, back_populates="contributors"
    )
    seasonings: Mapped[List[Seasoning]] = relationship(
        secondary=contrib_seasoning, back_populates="contributors"
    )
    mixins: Mapped[List[Mixin]] = relationship(
        secondary=contrib_mixin, back_populates="contributors"
    )
    condiments: Mapped[List[Condiment]] = relationship(
        secondary=contrib_condiment, back_populates="contributors"
    )
    base_layers: Mapped[List[BaseLayer]] = relationship(
        secondary=contrib_baselayer, back_populates="contributors"
    )
    
    def __repr__(self) -> str:
        return f'<Contributor {self.username!r}>'

    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SyncMetadata(db.Model):
    __tablename__ = 'sync_metadata'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sync_type: Mapped[str] = mapped_column(String(50))  # 'contributors', 'recipes', etc.
    last_commit_sha: Mapped[Optional[str]] = mapped_column(String(40))
    last_sync_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<SyncMetadata {self.sync_type}: {self.last_commit_sha}>'


# Mapper for API endpoints
MAPPER = {
    'base_layers': BaseLayer,
    'condiments': Condiment, 
    'mixins': Mixin,
    'seasonings': Seasoning,
    'shells': Shell
}