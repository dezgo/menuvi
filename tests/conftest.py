import pytest

from menuvi import create_app
from menuvi.config import Config
from menuvi.models import db as _db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"
    ADMIN_PASSWORD = "testpass"
    RESTAURANT_NAME = "Test Restaurant"
    RESTAURANT_TAGLINE = "Test Tagline"
    BRAND_COLOR = "#c9a84c"
    BRAND_COLOR_DIM = "#a68939"


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    with app.app_context():
        yield _db
