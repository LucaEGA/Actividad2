import pytest
from app import create_app, db
from app.models import User, Product, InventoryMovement, PredictorStockData

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app(config_class='app.config.Config') # Use base config
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite for tests
        "WTF_CSRF_ENABLED": False, # Disable CSRF for simpler form testing if forms were used directly
        "SECRET_KEY": "test-secret-key" # Consistent secret key for tests
    })
    with app.app_context():
        db.create_all() # Create all tables
        yield app # an app object for the tests
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture()
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture()
def init_database(app):
    """Clear and recreate database for each test function if needed (or manage per test)."""
    with app.app_context():
        # db.drop_all() # Not needed if session scope app fixture drops at end
        # db.create_all()
        yield db # The db instance
        # Clean up: delete all data from tables after each test
        # For more complex scenarios, transactions might be better
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def auth_client(client, init_database):
    """A test client that is pre-authenticated."""
    # Register a new user
    client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    # Login the user
    response = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    token = response.json['token']

    # Add a property to the client to easily get headers
    client.auth_headers = {
        'Authorization': f'Bearer {token}'
    }
    return client
