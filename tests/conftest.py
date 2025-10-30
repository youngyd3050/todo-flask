import pytest
from app import create_app, db
from app.models import User, Task
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    u = User(username='test', email='t@t.com', password=generate_password_hash('123'))
    db.session.add(u)
    db.session.commit()
    return u