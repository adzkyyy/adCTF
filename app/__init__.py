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
import threading
import time
import datetime
import pytz

# Configure PyMySQL to work with SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__, template_folder='../templates')
app.static_folder = '../static'
app.config.from_object(Config)

db = SQLAlchemy(app)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)

CORS(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Simplified SocketIO setup
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
    if request.path.startswith('/api/'):
        return jsonify({"error": "Not found"}), 404
    else:
        return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error"}), 500
    else:
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('index'))

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error for debugging
    print(f"Unhandled exception: {e}")
    db.session.rollback()
    
    # Return JSON error response
    if request.path.startswith('/api/'):
        return jsonify({"error": "An unexpected error occurred"}), 500
    else:
        # For non-API requests, redirect to a safe page
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# Simple tick scheduler function (kept as fallback)
def tick_scheduler():
    """Background thread that runs the tick system with precise timing"""
    import math
    
    print("Tick scheduler thread started")
    
    while True:
        try:
            with app.app_context():
                from app.models import Config, Tick
                from app.controllers.tick_controller import next_tick
                
                config = Config.query.first()
                if config and config.challenge_started:
                    # Get the last tick to determine next scheduled time
                    last_tick = Tick.query.order_by(Tick.id.desc()).first()
                    
                    if last_tick:
                        # Calculate when the next tick should occur
                        next_tick_time = last_tick.created_at.timestamp() + config.tick_duration_seconds
                        current_time = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).timestamp()
                        
                        # If it's time for the next tick (or overdue)
                        if current_time >= next_tick_time:
                            print(f"Scheduler: Executing scheduled tick at {datetime.datetime.now(pytz.timezone('Asia/Jakarta'))}")
                            result = next_tick()
                            print(f"Scheduler: {result}")
                            
                            # Sleep for a short interval before checking again
                            time.sleep(1)
                        else:
                            # Calculate how long to sleep until next tick
                            sleep_duration = min(next_tick_time - current_time, 5)  # Max 5 seconds
                            time.sleep(sleep_duration)
                    else:
                        # No ticks yet, check if we should start
                        print("Scheduler: No ticks found, waiting for manual start or checking in 5 seconds")
                        time.sleep(5)
                else:
                    # If challenge not started, check every 5 seconds
                    time.sleep(5)
                    
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(10)  # Wait 10 seconds before retrying on error

# Global variable to track if scheduler is running
scheduler_thread = None

def start_tick_scheduler():
    """Start the precise tick scheduler"""
    try:
        from app.tick_scheduler import get_scheduler
        scheduler = get_scheduler(app, db)
        return scheduler.start_challenge()
    except Exception as e:
        print(f"Error starting APScheduler: {e}")
        # Fallback to simple scheduler if APScheduler not available
        print("Using fallback scheduler")
        global scheduler_thread
        if scheduler_thread is None or not scheduler_thread.is_alive():
            scheduler_thread = threading.Thread(target=tick_scheduler, daemon=True)
            scheduler_thread.start()
            print("Fallback tick scheduler started")
        return True

def start_challenge_with_first_tick():
    """Start the challenge and execute the first tick immediately"""
    return start_tick_scheduler()

def stop_tick_scheduler():
    """Stop the tick scheduler"""
    try:
        from app.tick_scheduler import get_scheduler
        scheduler = get_scheduler(app, db)
        scheduler.stop_scheduling()
    except:
        pass

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