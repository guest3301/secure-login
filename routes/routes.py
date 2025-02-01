from flask import Blueprint, request, jsonify
from flask_limiter.util import get_remote_address 
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    current_user,
    set_access_cookies,
    unset_jwt_cookies
)
from flask_limiter import Limiter
from models import User, db, TokenBlocklist
from helpers.response import make_response, handle_error
from helpers.genqr import generate_qr_code_base64
import pyotp
import requests
from datetime import datetime, timezone

main_bp = Blueprint('main', __name__)
limiter = Limiter(key_func=get_remote_address, default_limits=["5 per minute"])

# ======================== REGISTER ROUTE ========================
@main_bp.route("/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return handle_error("Username and password required", 400)
    
    if User.query.filter_by(username=username).first():
        return handle_error("Username already exists", 409)
    
    try:
        new_user = User(username=username)
        new_user.set_password(password)
        new_user.otp_secret = pyotp.random_base32()  # Generate OTP secret on registration
        new_user.generate_backup_codes()
        db.session.add(new_user)
        db.session.commit()
        
        # Auto-login after registration
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))
        otp_uri = pyotp.totp.TOTP(new_user.otp_secret).provisioning_uri(
        name=new_user.username, issuer_name="SecureLoginApp"
    )
        qr_code_base64 = generate_qr_code_base64(otp_uri)
    
        return make_response(True, "Registration successful", {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "qr_code_base64": qr_code_base64,
        "otp_secret": new_user.otp_secret,
        "backup_codes": new_user.backup_codes
        })
    except Exception as e:
        db.session.rollback()
        return handle_error(str(e), 500)

# ======================== LOGOUT ROUTE ========================
@main_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    
    try:
        revoked_token = TokenBlocklist(jti=jti, created_at=now)
        db.session.add(revoked_token)
        db.session.commit()
        return make_response(True, "Successfully logged out")
    except Exception as e:
        db.session.rollback()
        return handle_error(str(e), 500)

# ======================== EXISTING ROUTES BELOW ========================
# (Keep your existing login, verify-otp, refresh, protected, and setup-2fa routes)
# Helper: Check time/location
def check_time_location(user):
    now = datetime.now().time()
    start = datetime.strptime(user.usual_login_times["start"], "%H:%M").time()
    end = datetime.strptime(user.usual_login_times["end"], "%H:%M").time()
    if not (start <= now <= end):
        return False
    
    ip = request.remote_addr
    location = requests.get(f"https://ipinfo.io/{ip}/json").json().get("city", "")
    return location in user.trusted_locations

# Route: Login (Step 1)
@main_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    
    if not user or not user.check_password(data.get("password", "")):
        return handle_error("Invalid credentials", 401)
    
    # Biometric check (mock)
    if user.biometric_enabled and not data.get("biometric_token"):
        return jsonify({
            "success": False,
            "action_required": "biometric",
            "partial_token": create_access_token(identity=str(user.id), fresh=False)  # Temp token
        }), 403
    
    # Time/location check
    if not check_time_location(user):
        return jsonify({
            "success": False,
            "action_required": "otp",
            "partial_token": create_access_token(identity=str(user.id), fresh=False)  # Temp token
        }), 403
    
    # Full login successful
    access_token = create_access_token(identity=str(user.id), fresh=True)
    refresh_token = create_refresh_token(identity=str(user.id))
    return make_response(True, "Logged in", {
        "access_token": access_token,
        "refresh_token": refresh_token
    })

# Route: Verify OTP (Step 2)
@main_bp.route("/verify-otp", methods=["POST"])
@jwt_required(fresh=False)  # Requires non-fresh token (from partial login)
def verify_otp():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    otp = request.json.get("otp", "")
    backup_code = request.json.get("backup_code", "")
    
    if pyotp.TOTP(user.otp_secret).verify(otp) or (backup_code in user.backup_codes):
        # Invalidate backup code after use
        if backup_code:
            user.backup_codes.remove(backup_code)
            db.session.commit()
        
        # Issue fresh tokens
        access_token = create_access_token(identity=str(user_id), fresh=True)
        refresh_token = create_refresh_token(identity=str(user_id))
        return make_response(True, "2FA verified", {
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
    return handle_error("Invalid OTP/backup code", 401)

# Route: Refresh Token
@main_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(user_id), fresh=False)
    return make_response(True, "Token refreshed", {"access_token": new_access_token})

# Route: Protected Endpoint
@main_bp.route("/protected")
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return make_response(True, f"Hello, user {user_id}")

# Route: Setup 2FA
@main_bp.route("/setup-2fa", methods=["POST"])
@jwt_required()
def setup_2fa():
    user = db.session.get(User, get_jwt_identity())
    user.otp_secret = pyotp.random_base32()
    user.backup_codes = [pyotp.random_base32() for _ in range(10)]
    db.session.commit()
    
    otp_uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(
    name=user.username, issuer_name="SecureLoginApp"
    )
    qr_code_base64 = generate_qr_code_base64(otp_uri)
    
    return make_response(True, "2FA setup complete", {
        "qr_code_base64": qr_code_base64,
        "otp_secret": user.otp_secret,
        "backup_codes": user.backup_codes
    })
