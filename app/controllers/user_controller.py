# user_controller.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, db
from app.models import User
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/api/user', methods=['GET'])
def api_user():
    users = User.query.filter(User.is_admin == False).all()

    users_list = [user.serialize() for user in users]
    return jsonify(users_list), 200

@app.route('/admin/user', methods=['GET'])
@login_required
def user():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('public_index'))
    
    users = User.query.filter(User.is_admin == False).all()
    return render_template('admin/user_management.html', users=users)

@app.route('/admin/user', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('public_index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    host_ip = request.form.get('host_ip')
    
    user = User(username=username, password_hash=generate_password_hash(password), host_ip=host_ip)
    db.session.add(user)
    db.session.commit()
    
    flash('User added successfully!', 'success')
    return 'User added successfully!'

@app.route('/admin/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'You do not have permission to access this page.'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting admin users
        if user.is_admin:
            return jsonify({'error': 'Cannot delete admin users.'}), 400
        
        # Prevent users from deleting themselves
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account.'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user {user_id}: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting the user.'}), 500

@app.route('/admin/user/<int:user_id>', methods=['PUT'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('public_index'))
    
    user = User.query.get_or_404(user_id)
    username = request.form.get('username')
    host_ip = request.form.get('host_ip')
    password = request.form.get('password')

    if username:
        user.username = username
    if host_ip:
        user.host_ip = host_ip
    if password:
        user.password_hash = generate_password_hash(password)

    db.session.commit()
    
    flash('User updated successfully!', 'success')
    return 'User updated successfully!'

@app.route('/admin/user/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('public_index'))
    
    user = User.query.get_or_404(user_id)
    password = request.form.get('password')
    
    if password:
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        flash('Password reset successfully!', 'success')
        return 'Password reset successfully!'
    else:
        return 'Password is required!', 400

import json

@app.route('/admin/user/import', methods=['POST'])
@login_required
def import_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('public_index'))
    
    if 'file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('user'))

    file = request.files['file']

    if file.filename == '' or not file.filename.endswith('.json'):
        flash('Invalid file format! Please upload a JSON file.', 'error')
        return redirect(url_for('user'))

    try:
        json_data = json.load(file)
    except Exception as e:
        flash('Error reading JSON file: {}'.format(str(e)), 'error')
        return redirect(url_for('user'))

    print(json_data)

    if not isinstance(json_data, list):
        flash('Invalid JSON format! Please provide a list of user objects.', 'error')
        return redirect(url_for('user'))

    for user_data in json_data:
        if not isinstance(user_data, dict):
            flash('Invalid user data format! Skipping user because not a dict: ' + user_data, 'warning')
            continue

        username = user_data.get('username')
        password_hash = user_data.get('password_hash')
        host_ip = user_data.get('host_ip')

        if not all([username, password_hash, host_ip]):
            flash('Incomplete user data! Skipping user because invalid format: ' + user_data, 'warning')
            continue

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User "{}" already exists! Skipping user.'.format(username), 'warning')
            continue

        new_user = User(username=username, password_hash=password_hash, host_ip=host_ip)
        db.session.add(new_user)

    db.session.commit()

    flash('Users imported successfully!', 'success')
    return redirect(url_for('user'))

@app.route('/admin/user/export', methods=['GET'])
@login_required
def export_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('public_index'))
    
    users = User.query.filter(User.is_admin == False).all()
    user_data = [{'username': user.username, 'password_hash': user.password_hash ,'host_ip': user.host_ip} for user in users]
    
    # Convert user data to JSON format
    json_data = json.dumps(user_data, indent=4)
    
    # Set response headers for file download
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=users.json'}
    )
    
    return response

@app.route('/admin/user/reset-all-passwords', methods=['POST'])
@login_required
def reset_all_passwords():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('public_index'))
    
    default_password = request.form.get('password', 'defaultpassword')
    password_hash = generate_password_hash(default_password)
    
    # Reset passwords for all non-admin users
    users = User.query.filter(User.is_admin == False).all()
    for user in users:
        user.password_hash = password_hash
    
    db.session.commit()
    
    return jsonify({
        'message': f'Passwords reset for {len(users)} users',
        'users_affected': len(users)
    })

# Test endpoint to verify DELETE method is working
@app.route('/admin/user/test-delete/<int:user_id>', methods=['DELETE'])
@login_required
def test_delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'message': f'Test DELETE endpoint called for user {user_id}',
        'method': request.method,
        'user_id': user_id
    }), 200
