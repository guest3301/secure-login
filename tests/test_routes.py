import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user
from models import User
from routes.routes import main_bp
import pyotp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        user = User(username='testuser')
        user.set_password('testpassword')
        user.otp_secret = pyotp.random_base32()
        db.session.add(user)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/register', json={
        'username': 'newuser',
        'password': 'newpassword'
    })
    assert response.status_code == 200
    assert 'Successfully registered.' in response.get_data(as_text=True)

def test_login(client, app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        totp = pyotp.TOTP(user.otp_secret)
        otp = totp.now()

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword',
        'otp': otp
    })
    assert response.status_code == 200
    assert 'Successfully logged in.' in response.get_data(as_text=True)

def test_logout(client, app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        login_user(user)

    response = client.get('/logout')
    assert response.status_code == 302
    assert '/login' in response.location
