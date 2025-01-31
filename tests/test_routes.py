import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user
from models import User, db
from routes.routes import main_bp
import pyotp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    db.init_app(app)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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
        totp = pyotp.TOTP(user.otp_secret)
        otp = totp.now()

    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword',
        'otp': otp
    })
    assert login_response.status_code == 200

    logout_response = client.get('/logout', follow_redirects=True)
    assert logout_response.status_code == 200
    assert 'Logged out.' in logout_response.get_data(as_text=True)
