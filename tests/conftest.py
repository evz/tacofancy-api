import pytest
from app import create_app
from app.config import TestingConfig
from app.models import db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(autouse=True)
def setup_db(app):
    """Setup database for each test with transaction rollback."""
    with app.app_context():
        # Start a nested transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure the session to use the connection
        db.session.configure(bind=connection)
        
        yield
        
        # Rollback the transaction
        transaction.rollback()
        connection.close()
        db.session.remove()