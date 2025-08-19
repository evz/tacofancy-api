import logging

import click
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from .config import Config
from .models import db


def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    Migrate(app, db)

    # Setup Flask-RESTful API
    from .api import setup_api

    setup_api(app)

    # Register template routes (for web interface)
    from .routes import template_routes

    app.register_blueprint(template_routes)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import make_response

        return make_response({"error": "Not found"}, 404)

    @app.errorhandler(500)
    def internal_error(error):
        from flask import make_response

        return make_response({"error": "Internal server error"}, 500)

    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database tables created.")

    @app.cli.command()
    def load_recipes():
        """Load recipe data from GitHub."""
        from .github_loader import load_tacofancy_data

        print("Loading recipe data from GitHub...")
        try:
            load_tacofancy_data(app.config["GITHUB_TOKEN"], include_contributors=False)
            print("Successfully loaded recipe data!")
        except Exception as e:
            print(f"Error loading recipes: {e}")
            raise

    @app.cli.command()
    @click.option("--full", is_flag=True, help="Do a full sync instead of incremental")
    def load_contributors(full):
        """Load contributor data from GitHub."""
        from .github_loader import TacoFancyLoader

        sync_type = "full" if full else "incremental"
        print(f"Loading contributor data from GitHub ({sync_type} sync)...")
        try:
            loader = TacoFancyLoader(app.config["GITHUB_TOKEN"])
            loader.load_contributors(incremental=not full)
            print("Successfully loaded contributor data!")
        except Exception as e:
            print(f"Error loading contributors: {e}")
            raise

    @app.cli.command()
    @click.option("--full", is_flag=True, help="Do a full sync instead of incremental")
    def load_all(full):
        """Load all data (recipes and contributors) from GitHub."""
        from .github_loader import load_tacofancy_data

        sync_type = "full" if full else "incremental"
        print(f"Loading all data from GitHub ({sync_type} sync)...")
        try:
            load_tacofancy_data(
                app.config["GITHUB_TOKEN"],
                include_contributors=True,
                incremental=not full,
            )
            print("Successfully loaded all data!")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    @app.cli.command()
    def test():
        """Run the test suite."""
        import sys

        import pytest

        # Run pytest with verbose output
        exit_code = pytest.main(["-v", "tests/"])
        sys.exit(exit_code)

    # Configure logging
    configure_logging(app)

    return app


def configure_logging(app):
    """Configure application logging."""
    if app.debug:
        # Development logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        # Production logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # Set specific log levels for third-party libraries
    logging.getLogger("github").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.INFO)
