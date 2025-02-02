from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    otp_secret = db.Column(db.String(16))
    biometric_enabled = db.Column(db.Boolean, default=False)
    trusted_locations = db.Column(db.JSON, default=[])  # Initialize as empty list
    usual_login_times = db.Column(db.JSON, default={"start": "00:00", "end": "23:59"})  # Default: allow all times
    backup_codes = db.Column(db.JSON, default=[])

    def set_password(self, password):
        """
        Set the password for the user.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if the provided password matches the stored password hash.
        """
        return check_password_hash(self.password_hash, password)

    def generate_backup_codes(self):
        """
        Generate a list of backup codes for the user.
        """
        self.backup_codes = [pyotp.random_base32() for _ in range(10)]

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
