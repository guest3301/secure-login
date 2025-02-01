import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from models import User, db, TokenBlocklist
from routes.routes import main_bp
import pyotp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    app.config['TESTING'] = True
    db.init_app(app)
    jwt = JWTManager(app)

    # Register the main blueprint
    app.register_blueprint(main_bp)

    # Create the database and add a test user
    with app.app_context():
        db.create_all()
        user = User(username='testuser')
        user.set_password('testpassword')
        user.otp_secret = pyotp.random_base32()
        user.generate_backup_codes()
        db.session.add(user)
        db.session.commit()

    yield app

    # Clean up the database after tests
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
    data = response.get_json()
    assert data['success'] is True
    assert data['message'] == "Registration successful"
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']
    assert 'qr_code_base64' in data['data']
    assert 'otp_secret' in data['data']
    assert 'backup_codes' in data['data']

def test_login(client, app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        totp = pyotp.TOTP(user.otp_secret)
        otp = totp.now()

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 403  # OTP required
    data = response.get_json()
    assert data['success'] is False
    assert data['action_required'] == "otp"
    assert 'partial_token' in data

    # Verify OTP
    partial_token = data['partial_token']
    verify_response = client.post('/verify-otp', json={
        'otp': otp
    }, headers={'Authorization': f'Bearer {partial_token}'})
    assert verify_response.status_code == 200
    verify_data = verify_response.get_json()
    assert verify_data['success'] is True
    assert verify_data['message'] == "2FA verified"
    assert 'access_token' in verify_data['data']
    assert 'refresh_token' in verify_data['data']

def test_logout(client, app):
    # TODO Implement this test
    pass

def test_setup_2fa(client, app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        totp = pyotp.TOTP(user.otp_secret)
        otp = totp.now()

    # Login and get access token
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    partial_token = login_response.get_json()['partial_token']
    verify_response = client.post('/verify-otp', json={
        'otp': otp
    }, headers={'Authorization': f'Bearer {partial_token}'})
    access_token = verify_response.get_json()['data']['access_token']

    # Setup 2FA
    setup_response = client.post('/setup-2fa', headers={'Authorization': f'Bearer {access_token}'})
    assert setup_response.status_code == 200
    setup_data = setup_response.get_json()
    assert setup_data['success'] is True
    assert setup_data['message'] == "2FA setup complete"
    assert 'qr_code_base64' in setup_data['data']
    assert 'otp_secret' in setup_data['data']
    assert 'backup_codes' in setup_data['data']

def test_protected_route(client, app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        totp = pyotp.TOTP(user.otp_secret)
        otp = totp.now()

    # Login and get access token
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    partial_token = login_response.get_json()['partial_token']
    verify_response = client.post('/verify-otp', json={
        'otp': otp
    }, headers={'Authorization': f'Bearer {partial_token}'})
    access_token = verify_response.get_json()['data']['access_token']

    # Access protected route
    protected_response = client.get('/protected', headers={'Authorization': f'Bearer {access_token}'})
    assert protected_response.status_code == 200
    protected_data = protected_response.get_json()
    assert protected_data['success'] is True
    assert protected_data['message'] == f"Hello, user {user.id}"