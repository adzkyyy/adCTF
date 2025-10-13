# challenge_controller.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, db
from app.models import Challenge, User, Submission
from flask_login import login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import requests
import os

load_dotenv()

@app.route('/api/challenges', methods=['GET'])
@jwt_required()
def api_challenges():
    username = get_jwt_identity()
    current_user = User.query.filter_by(username=username).first()
    challenges = Challenge.query.all()
    challenges_list = [challenge.serialize(user_id=current_user.id) for challenge in challenges]
    return jsonify(challenges_list), 200

@app.route('/api/restart/<string:challenge>', methods=['POST'])
@jwt_required()
def restart_challenge(challenge):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    url = 'http://' + user.host_ip + '/restart/' + challenge

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to restart challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": "An error occurred:" + str(e)}), 500

@app.route('/api/rollback/<string:challenge>', methods=['POST'])
@jwt_required()
def rollback_challenge(challenge):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    url = 'http://' + user.host_ip + '/rollback/' + challenge

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to rollback challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": "An error occurred:" + str(e)}), 500
    
@app.route('/api/activate/<string:challenge>', methods=['POST'])
@jwt_required()
def activate_challenge(challenge):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    url = 'http://' + user.host_ip + '/activate/' + challenge

    try:
        print("aaaa")
        print(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to activate challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": "An error occurred:" + str(e)}), 500

@app.route('/api/deactivate/<string:challenge>', methods=['POST'])
@jwt_required()
def deactivate_challenge(challenge):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    url = 'http://' + user.host_ip + '/deactivate/' + challenge

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to deactivate challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": "An error occurred:" + str(e)}), 500

@app.route('/api/credential/<string:challenge>', methods=['GET'])
@jwt_required()
def challenge_credential(challenge):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    challengeObj = Challenge.query.filter_by(name=challenge).first()
    if not challengeObj:
        return jsonify({"message": "Failed to fetch challenge credential.", "status_code": 400}), 400
    
    if not challengeObj.is_solved_by_user(user.id):
        return jsonify({"message": "Failed to fetch challenge credential.", "status_code": 400}), 400
    
    url = 'http://' + user.host_ip + '/credential/' + challenge

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to fetch challenge credential.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": "An error occurred:" + str(e)}), 500

# Session-based routes (for web interface)
@app.route('/challenges/restart/<string:challenge>', methods=['POST'])
@login_required
def session_restart_challenge(challenge):
    # Debug logging
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    print(f"DEBUG: Current user: {current_user.username}")
    print(f"DEBUG: Current user host_ip: {current_user.host_ip}")
    
    url = 'http://' + current_user.host_ip + '/restart/' + challenge
    print(f"DEBUG: Restarting {challenge} at {url}")
    print(f"DEBUG: Using credentials - Username: {admin_username}, Password: {admin_password}")

    try:
        response = requests.get(url, auth=(admin_username, admin_password))
        print(f"DEBUG: Response status: {response.status_code}")
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            print(f"DEBUG: Response text: {response.text}")
            if response.status_code == 401:
                return jsonify({
                    "message": f"Authentication failed. Server at {current_user.host_ip} rejected credentials. Please check ADMIN_USERNAME and ADMIN_PASSWORD in .env file.",
                    "status_code": response.status_code,
                    "detail": response.text
                }), response.status_code
            else:
                return jsonify({"message": "Failed to restart challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        print(f"DEBUG: Request exception: {str(e)}")
        return jsonify({"message": "An error occurred:" + str(e)}), 500

@app.route('/challenges/rollback/<string:challenge>', methods=['POST'])
@login_required
def session_rollback_challenge(challenge):
    # Debug logging
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    print(f"DEBUG: Current user: {current_user.username}")
    print(f"DEBUG: Current user host_ip: {current_user.host_ip}")
    
    url = 'http://' + current_user.host_ip + '/rollback/' + challenge
    print(f"DEBUG: Rolling back {challenge} at {url}")
    print(f"DEBUG: Using credentials - Username: {admin_username}, Password: {admin_password}")

    try:
        response = requests.get(url, auth=(admin_username, admin_password))
        print(f"DEBUG: Response status: {response.status_code}")
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            print(f"DEBUG: Response text: {response.text}")
            if response.status_code == 401:
                return jsonify({
                    "message": f"Authentication failed. Server at {current_user.host_ip} rejected credentials. Please check ADMIN_USERNAME and ADMIN_PASSWORD in .env file.",
                    "status_code": response.status_code,
                    "detail": response.text
                }), response.status_code
            else:
                return jsonify({"message": "Failed to rollback challenge.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        print(f"DEBUG: Request exception: {str(e)}")
        return jsonify({"message": "An error occurred:" + str(e)}), 500

@app.route('/challenges/credential/<string:challenge>', methods=['GET'])
@login_required
def session_challenge_credential(challenge):
    challengeObj = Challenge.query.filter_by(name=challenge).first()
    if not challengeObj:
        return jsonify({"message": "Failed to fetch challenge credential.", "status_code": 400}), 400
    
    if not challengeObj.is_solved_by_user(current_user.id):
        return jsonify({"message": "Failed to fetch challenge credential.", "status_code": 400}), 400
    
    url = 'http://' + current_user.host_ip + '/credential/' + challenge

    try:
        response = requests.get(url, auth=(os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')))
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "Failed to fetch challenge credential.", "status_code": response.status_code}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": "An error occurred:" + str(e)}), 500

@app.route('/admin/challenges', methods=['GET'])
@login_required
def challenges():
    challenges = Challenge.query.all()
    return render_template('admin/challenge_management.html', challenges=challenges)

@app.route('/admin/challenge', methods=['POST'])
@login_required
def add_challenge():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    name = request.form.get('name')
    title = request.form.get('title')
    port = request.form.get('port')
    description = request.form.get('description')
    category = request.form.get('category', 'general')
    
    challenge = Challenge(name=name, title=title, port=port, description=description, category=category)
    db.session.add(challenge)
    db.session.commit()
    
    flash('Challenge added successfully!', 'success')
    return 'Challenge added successfully!'

@app.route('/admin/challenge/<int:challenge_id>', methods=['DELETE'])
@login_required
def delete_challenge(challenge_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    
    return 'Challenge deleted successfully!'

@app.route('/admin/challenge/<int:challenge_id>', methods=['PUT'])
@login_required
def edit_challenge(challenge_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)    
    challenge.name = request.form.get('name')
    challenge.title = request.form.get('title')
    challenge.port = request.form.get('port')
    challenge.description = request.form.get('description')
    challenge.category = request.form.get('category', challenge.category or 'general')

    db.session.commit()
    
    flash('Challenge updated successfully!', 'success')
    return 'Challenge updated successfully!'

import json


@app.route('/admin/challenge/import', methods=['POST'])
@login_required
def import_challenges():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    if 'file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('challenges'))

    file = request.files['file']

    if file.filename == '' or not file.filename.endswith('.json'):
        flash('Invalid file format! Please upload a JSON file.', 'error')
        return redirect(url_for('challenges'))

    try:
        json_data = json.load(file)
    except Exception as e:
        flash('Error reading JSON file: {}'.format(str(e)), 'error')
        return redirect(url_for('challenges'))

    print(json_data)

    if not isinstance(json_data, list):
        flash('Invalid JSON format! Please provide a list of user objects.', 'error')
        return redirect(url_for('challenges'))

    for challenge_data in json_data:
        if not isinstance(challenge_data, dict):
            flash('Invalid challenge data format! Skipping challenge because not a dict: ' + challenge_data, 'warning')
            continue

        name = challenge_data.get('name')
        title = challenge_data.get('title')
        port = challenge_data.get('port')
        description = challenge_data.get('description')

        if not all([name, title, port, description]):
            flash('Incomplete challenge data ! Skipping challenge because invalid format: ' + challenge_data, 'warning')
            continue

        existing_challenge = Challenge.query.filter_by(name=name).first()
        if existing_challenge:
            flash('Challenge with name "{}" already exists! Skipping challenge.'.format(name), 'warning')
            continue
        
        existing_challenge = Challenge.query.filter_by(port=port).first()
        if existing_challenge:
            flash('Challenge with port "{}" already exists! Skipping challenge.'.format(port), 'warning')
            continue

        new_challenge = Challenge(name=name, title=title, port=port, description=description)
        db.session.add(new_challenge)

    db.session.commit()

    flash('Challenges imported successfully!', 'success')
    return redirect(url_for('challenges'))

@app.route('/admin/challenge/export', methods=['GET'])
@login_required
def export_challenges():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    challenges = Challenge.query.all()
    challenge_data = [{'name': challenge.name, 'title': challenge.title, 'port': challenge.port ,'description': challenge.description} for challenge in challenges]
    
    json_data = json.dumps(challenge_data, indent=4)
    
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=challenges.json'}
    )
    
    return response