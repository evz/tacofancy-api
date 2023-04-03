import os

import click

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///tacofancy.db"
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from .db import db, init_db_command

    db.init_app(app)
    app.cli.add_command(init_db_command)
    
    from .commands import preheat
    app.cli.add_command(preheat)

    return app
