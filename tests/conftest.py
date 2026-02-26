import pytest

from menuvi import create_app
from menuvi.config import Config
from menuvi.models import db as _db, Restaurant, User


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"
    LOGIN_DISABLED = False


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


@pytest.fixture()
def restaurant(db):
    r = Restaurant(
        name="Test Restaurant",
        slug="test-restaurant",
        tagline="Test Tagline",
        brand_color="#c9a84c",
        brand_color_dim="#a68939",
    )
    db.session.add(r)
    db.session.commit()
    return r


@pytest.fixture()
def admin_user(db, restaurant):
    user = User(email="admin@test.com", role="owner", restaurant_id=restaurant.id)
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def superadmin_user(db):
    user = User(email="super@test.com", role="superadmin")
    user.set_password("superpass")
    db.session.add(user)
    db.session.commit()
    return user
