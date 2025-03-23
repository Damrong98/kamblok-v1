# auth.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
# from models.userModel import User
from App.models.models import User, UserMessageLimit
from App.models.system_settings import SystemSettings
from App.database import db
from utils import login_required
from datetime import date, datetime

auth_bp = Blueprint('auth', __name__)

def get_user_message_limit(user_id):
    today = date.today()
    
    # Query the user's message limit for today
    limit = UserMessageLimit.query.filter_by(
        user_id=user_id,
        date=today
    ).first()
    
    # If no record exists for today, they haven't sent any messages yet
    if not limit:
        return 0  # 0 messages sent out of 10
    
    return limit.message_count  # Return current count out of 10


# View route (GET)
@auth_bp.route('/users/<auth_id>', methods=['GET'])
@login_required
def get_auth(auth_id):
    user = User.query.get_or_404(auth_id)
    current_user = User.query.get_or_404(auth_id)
    message_limit = get_user_message_limit(current_user.id)
    system_settings = SystemSettings.query.first()

    max_messages_today = current_user.max_messages + system_settings.max_messages
    user_data = {
        'max_messages_today' : max_messages_today,
        'message_limit' : message_limit,
    }
    return render_template('auth/auth_settings.html', user=user, user_data=user_data)

# API route (POST)
@auth_bp.route('/users/<auth_id>/update', methods=['POST'])
@login_required
def user_update_api(auth_id):
    data = request.get_json()
    user = User.query.get_or_404(auth_id)
    
    try:
        field = data['field']
        value = data['value']

        if field == 'first_name':
            user.first_name = value
        elif field == 'last_name':
            user.last_name = value
        elif field == 'username':
            if User.query.filter(User.username == value, User.id != user.id).first():
                return jsonify({'success': False, 'error': 'Username already taken'})
            user.username = value
        elif field == 'date_of_birth':
            user.date_of_birth = datetime.strptime(value, '%Y-%m-%d').date() if value else None
        elif field == 'phone_number':
            if User.query.filter(User.phone_number == value, User.id != user.id).first():
                return jsonify({'success': False, 'error': 'Phone number already taken'})
            user.phone_number = value
        elif field == 'email':
            if User.query.filter(User.email == value, User.id != user.id).first():
                return jsonify({'success': False, 'error': 'Email already taken'})
            user.email = value
        elif field == 'password':
            user.set_password(value)
        elif field == 'picture':
            user.picture = value
        # elif field == 'role':
        #     user.role = int(value)
        # elif field == 'max_messages':
        #     user.max_messages = int(value)

        db.session.commit()
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    



"""
Route: Frontend
Return: render_template
"""  

# Route for the initial register page
@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('/auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        # print(f"Login attempt - Identifier: {identifier}, Password: {password}")
        
        # Check if the identifier matches either username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        try:
            if user and user.check_password(password):
                # Only access user attributes here, after confirming user exists
                # print(f"User: {user.username}, Email: {user.email}, Hash: {user.password_hash}, Check: {user.check_password(password)}")
                session['user_id'] = user.id
                session['user_role'] = user.role
                flash('Login successful', 'success')
                return redirect(url_for('user_conversation_routes.user_new_chat'))
            else:
                flash('Invalid credentials', 'error')
        except Exception as e:
            print("login Error:", e)
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

"""
Route: API
Return: jsonify
"""  

@auth_bp.route('/api/auth', methods=['GET'])
@login_required
def get_auth_api():
    # Get the current user from session
    current_user = User.query.get(session['user_id'])
    user_role = session.get('user_role')

    if current_user is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    message_limit = get_user_message_limit(current_user.id)

    system_settings = SystemSettings.query.first()

    max_messages_today = current_user.max_messages + system_settings.max_messages
    
    # Use session['user_picture'] if available, otherwise fall back to current_user.picture
    # final_picture = picture if picture is not None else current_user.picture #no need, set login picture to sesion instead
    
    user_data = {
        'id': current_user.id,
        'displayName' : current_user.first_name + " " + current_user.last_name,
        'username': current_user.username,
        'email': current_user.email,
        'picture': current_user.picture, 
        'role' : user_role,
        'max_messages' : current_user.max_messages,
        'max_messages_today' : max_messages_today,
        'message_limit' : message_limit,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None
    }
    
    # Return JSON response
    return jsonify({
        'status': 'success',
        'user': user_data
    })