from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from models import User, db
from helpers.response import make_response, handle_error
from flask_bcrypt import Bcrypt
import pyotp

main_bp = Blueprint('main', __name__)
bcrypt = Bcrypt()

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.json.get("username", "")
        password = request.json.get("password", "")
        remember = request.json.get("remember", False)
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            return make_response("Successfully logged in.", 200)
        else:
            return handle_error("Invalid username or password.", 401)
    else:
        if current_user.is_authenticated:
            return make_response("Already logged in.", 200)
        return make_response("Login page.", 200)

@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    # Hash the password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create new user
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@main_bp.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    user_id = session.get('temp_user_id')
    code = data.get('code')

    if not user_id or not code:
        return jsonify({"error": "User ID and 2FA code are required"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Verify 2FA code
    totp = pyotp.TOTP(user.otp_secret)
    if not totp.verify(code):
        return jsonify({"error": "Invalid 2FA code"}), 401

    session.pop('temp_user_id', None)
    login_user(user)
    return jsonify({"message": "2FA verification successful", "user_id": user.id}), 200

@main_bp.route('/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate a new secret key for 2FA
    secret = pyotp.random_base32()
    user.otp_secret = secret
    db.session.commit()

    # Generate a TOTP URI for the QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="YourAppName")

    return jsonify({"message": "2FA enabled", "secret": secret, "totp_uri": totp_uri}), 200

@main_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Disable 2FA
    user.otp_secret = None
    db.session.commit()

    return jsonify({"message": "2FA disabled"}), 200

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))