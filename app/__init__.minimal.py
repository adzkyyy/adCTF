# app/__init__.py

from flask import Flask, jsonify, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder='../templates')
app.static_folder = '../static'
app.config.from_object(Config)

db = SQLAlchemy(app)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)

CORS(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Simplified SocketIO setup without complex scheduling
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', engineio_logger=False, logger=False)

@socketio.on('connect')
def test_connect():
    try:
        emit('after connect', {'message': 'socket connected'})
    except Exception as e:
        print(f"SocketIO connect error: {e}")

@socketio.on_error_default
def default_error_handler(e):
    print(f"SocketIO error: {e}")
    return False

# Add error handlers to prevent unhandled exceptions
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error for debugging
    print(f"Unhandled exception: {e}")
    db.session.rollback()
    
    # Return JSON error response
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({"error": "An unexpected error occurred"}), 500
    else:
        # For non-API requests, redirect to a safe page
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# Import at the end to avoid circular imports
from app import models, views, controllers
from app.controllers import main_controller, auth_controller, user_controller, challenge_controller, tick_controller, flag_controller, score_controller

import os
from dotenv import load_dotenv

load_dotenv()

# Initialize database with basic setup
with app.app_context():
    try:
        # Check if an admin user exists
        admin_user = models.User.query.filter_by(is_admin=True).first()

        # If no admin user exists, create one
        if not admin_user:
            admin = models.User(
                username=os.getenv('ADMIN_USERNAME', 'admin'), 
                password_hash=generate_password_hash(os.getenv('ADMIN_PASSWORD', 'password')), 
                is_admin=True, 
                host_ip=""
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")
            
        # Check if a configuration row exists
        config = models.Config.query.first()

        # If no configuration exists, create one
        if not config:
            default_config = models.Config(
                challenge_started=False, 
                ticks_count=0, 
                tick_duration_seconds=60
            )
            db.session.add(default_config)
            db.session.commit()
            print("Default config created")
            
    except Exception as e:
        print(f"Initialization error: {e}")
        print("Make sure you ran 'python init_db.py' first")