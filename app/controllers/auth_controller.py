from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from app import app, db
from app.models import User

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('public_index'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    # Get context for navbar
    from app.models import Config
    config = Config.query.first()
    challenge_started = config.challenge_started if config else False
    
    context = {
        'challenge_started': challenge_started,
        'current_round_num': 0,
        'total_rounds': 0,
        'current_tick_num': 0,
        'total_ticks': 0
    }

    return render_template('public/login.html', **context)

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "Login failed. Please check your username and password."}), 401
    except Exception as e:
        print(f"Error in api_login: {e}")
        return jsonify({"msg": "An error occurred during login"}), 500

@app.route('/api/get-token', methods=['GET'])
@login_required
def get_current_user_token():
    """Get JWT token for current logged-in user"""
    try:
        if current_user.is_authenticated:
            access_token = create_access_token(identity=current_user.username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "User not authenticated"}), 401
    except Exception as e:
        print(f"Error in get_current_user_token: {e}")
        return jsonify({"msg": "An error occurred while generating token"}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public_index'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Get the current logged-in user
        user = User.query.get(current_user.id)

        # Check if the current password provided matches the user's password
        if not check_password_hash(user.password_hash, current_password):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('change_password'))

        # Check if the new password and confirmation match
        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'danger')
            return redirect(url_for('change_password'))

        # Generate password hash for the new password
        new_password_hash = generate_password_hash(new_password)

        # Update the user's password hash
        user.password_hash = new_password_hash
        db.session.commit()

        flash('Password changed successfully.', 'success')
        return redirect(url_for('public_index'))

    # Get context for navbar  
    from app.models import Config
    config = Config.query.first()
    challenge_started = config.challenge_started if config else False
    
    context = {
        'challenge_started': challenge_started,
        'current_round_num': 0,
        'total_rounds': 0,
        'current_tick_num': 0,
        'total_ticks': 0
    }

    return render_template('public/change_password.html', **context)
