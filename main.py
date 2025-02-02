from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address 
from models import db, TokenBlocklist
from dotenv import load_dotenv
import os
import threading
import subprocess

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES"))
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]

# Initialize extensions
jwt = JWTManager(app)
db.init_app(app)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["5 per minute"])

# JWT Blocklist Configuration
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None

# Register blueprints
from routes.routes import main_bp
app.register_blueprint(main_bp)

def start_serveo():
    subprocess.run(["ssh", "-R", "80:localhost:8000", "serveo.net"])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Start Serveo SSH in a separate thread
    threading.Thread(target=start_serveo).start()
    app.run(host="0.0.0.0", port=8000, debug=False)