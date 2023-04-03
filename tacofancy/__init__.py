import os

import click

from flask import Flask

from .routes import routes

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///tacofancy.db"


class ProdConfig(Config):
    pass


config_map = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig,
}


def create_app():
    app = Flask(__name__)
    config_name = os.getenv("ENV", "test")
    app.config.from_object(config_map[config_name])
    config_map[config_name].init_app(app)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from .db import db, init_db_command

    db.init_app(app)
    app.cli.add_command(init_db_command)
    
    from .commands import preheat
    app.cli.add_command(preheat)
    
    app.register_blueprint(routes)

    return app
