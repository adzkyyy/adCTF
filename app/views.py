# app/views.py

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app import app

@app.context_processor
def inject_challenge_info():
    """Inject challenge information into all templates"""
    try:
        from app.models import Config, Round, Tick
        config = Config.query.first()
        challenge_started = config.challenge_started if config else False
        ticks_count = config.ticks_count if config else 0
        
        last_round = Round.query.order_by(Round.id.desc()).first()
        last_tick = Tick.query.order_by(Tick.id.desc()).first()
        
        current_round_num = last_round.id if last_round else 0
        current_tick_num = last_tick.id if last_tick else 0
        
        # Calculate total rounds based on ticks (every 5 ticks = 1 round)
        total_rounds = (ticks_count + 4) // 5 if ticks_count > 0 else 0
        
        return {
            'challenge_started': challenge_started,
            'current_round_num': current_round_num,
            'total_rounds': total_rounds,
            'current_tick_num': current_tick_num,
            'total_ticks': ticks_count
        }
    except Exception as e:
        # If there's any error, return default values
        return {
            'challenge_started': False,
            'current_round_num': 0,
            'total_rounds': 0,
            'current_tick_num': 0,
            'total_ticks': 0
        }

@app.route('/')
def index():
    return redirect(url_for('public_index'))

@app.route('/home')
def public_index():
    """Public home page"""
    return render_template('public/index.html')

@app.route('/challenges')
@login_required
def public_services():
    """Protected challenges page - requires login"""
    from app.models import Config, Challenge
    config = Config.query.first()
    challenge_started = config.challenge_started if config else False
    
    if challenge_started:
        # Get all challenges and add solve status for current user
        challenges_raw = Challenge.query.all()
        challenges = []
        
        for challenge in challenges_raw:
            # Create a dictionary with challenge data and solve status
            challenge_data = {
                'id': challenge.id,
                'name': challenge.name,
                'title': challenge.title,
                'port': challenge.port,
                'description': challenge.description,
                'category': challenge.category,
                'is_solved': challenge.is_solved_by_user(current_user.id)
            }
            challenges.append(challenge_data)
    else:
        challenges = []
    
    return render_template('public/challenges.html', 
                         challenge_started=challenge_started,
                         challenges=challenges)

@app.route('/scoreboard')
@login_required
def public_scoreboard():
    """Protected scoreboard page - requires login"""
    from app.models import Config, User, Challenge, Round, Submission, Check
    config = Config.query.first()
    challenge_started = config.challenge_started if config else False
    
    # Get initial scoreboard data to avoid showing "no data" initially
    scoreboard_data = []
    if challenge_started:
        try:
            users = User.query.filter_by(is_admin=False).all()
            challenges = Challenge.query.all()
            last_round = Round.query.order_by(Round.id.desc()).first()

            for user in users:
                user_scores = {
                    "username": user.username,
                    "host_ip": user.host_ip,
                    "total_points": 0,
                    "attack_points": 0,
                    "defense_points": 0,
                    "attacks": {},
                    "defenses": {},
                    "flags": {},
                    "sla": {},
                    "passed_checks": {},
                    "total_checks": {}
                }
                
                for challenge in challenges:
                    # Calculate attack score
                    success_attacks = Submission.query.filter_by(attacker=user, chall_id=challenge.id).count()
                    # Calculate defense score
                    failed_defenses = Submission.query.filter_by(target=user, chall_id=challenge.id).count()
                    total_round = (last_round.id if last_round else 1)
                    defense_score = max(0, ((len(users) - 1) * total_round) - failed_defenses)
                    
                    user_scores["attacks"][challenge.name] = success_attacks
                    user_scores["defenses"][challenge.name] = defense_score
                    user_scores["flags"][challenge.name] = {"captured": success_attacks, "stolen": failed_defenses}
                    user_scores["sla"][challenge.name] = "DOWN"
                    user_scores["passed_checks"][challenge.name] = 0
                    user_scores["total_checks"][challenge.name] = 0

                checks = Check.query.filter_by(user_id=user.id).order_by(Check.tick_id.asc()).all()
                passed_checks = 0
                total_checks = 0

                for check in checks:
                    challenge = Challenge.query.get(check.chall_id)
                    if challenge:
                        challenge_name = challenge.name
                        user_scores["total_checks"][challenge_name] += 1
                        if check.status == "up":
                            user_scores["passed_checks"][challenge_name] += 1
                        user_scores["sla"][challenge_name] = check.status.upper()

                attack_points = 0
                defense_points = 0

                for challenge in challenges:            
                    challenge_name = challenge.name
                    attack_points += user_scores["attacks"][challenge_name]
                    defense_points += user_scores["defenses"][challenge_name]
                    passed_checks += user_scores["passed_checks"][challenge_name]
                    total_checks += user_scores["total_checks"][challenge_name]
                
                # Prevent division by zero
                availability_score = max(0.1, passed_checks / total_checks if total_checks > 0 else 0.1)
                    
                user_scores["total_points"] = (attack_points + defense_points) * availability_score
                user_scores["attack_points"] = attack_points
                user_scores["defense_points"] = defense_points

                scoreboard_data.append(user_scores)
            scoreboard_data.sort(key=lambda x: x['total_points'], reverse=True)
        except Exception as e:
            print(f"Error loading initial scoreboard data: {e}")
    
    return render_template('public/scoreboard.html', scoreboard_data=scoreboard_data)

@app.route('/api-docs')
@login_required
def public_api_docs():
    """Protected API documentation page - requires login"""
    return render_template('public/api-docs.html')

@app.route('/admin')
@login_required
def admin_index():
    """Admin dashboard"""
    if not current_user.is_admin:
        return redirect(url_for('public_index'))
    
    from app.models import Config, User, Challenge
    config = Config.query.first()
    total_users = User.query.count()
    total_challenges = Challenge.query.count()
    
    return render_template('admin/index.html',
                         config=config,
                         total_users=total_users,
                         total_challenges=total_challenges,
                         challenge_started=config.challenge_started if config else False)

@app.route('/admin/challenges')
@login_required
def admin_challenges():
    """Admin challenge management"""
    if not current_user.is_admin:
        return redirect(url_for('public_index'))
    
    from app.models import Challenge
    challenges = Challenge.query.all()
    
    return render_template('admin/challenge_management.html', challenges=challenges)

# Add routes for login, register, dashboard, etc.
