# auth.py
import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
# from models.userModel import User
from App.models.models import User, UserMessageLimit
from App.models.system_settings import SystemSettings
from database import db
from werkzeug.security import check_password_hash
from utils import login_required
from authlib.integrations.flask_client import OAuthError
from datetime import date

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

@auth_bp.route('/users/<auth_id>', methods=['GET'])
@login_required
def get_auth(auth_id):
    current_user = User.query.get_or_404(auth_id)
    message_limit = get_user_message_limit(current_user.id)
    system_settings = SystemSettings.query.first()

    max_messages_today = current_user.max_messages + system_settings.max_messages

    user_data = {
        'id': current_user.id,
        'displayName' : current_user.first_name + " " + current_user.last_name,
        'username': current_user.username,
        'email': current_user.email,
        'max_messages' : current_user.max_messages,
        'max_messages_today' : max_messages_today,
        'message_limit' : message_limit,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None
    }
    print('User', user_data)
    return render_template('auth/auth_settings.html', user=user_data)


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
        identifier = request.form.get('identifier')  # Changed from 'username' to 'identifier'
        password = request.form.get('password')
        print(f"Login attempt - Identifier: {identifier}, Password: {password}")
        # Check if the identifier matches either username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        print(f"User: {user.username}, Email: {user.email}, Hash: {user.password_hash}, Check, {user.check_password(password)}")
        try:
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_role'] = user.role
                flash('Login successful', 'success')
                return redirect(url_for('user_conversation_routes.user_new_chat'))
            else:
                flash('Invalid credentials', 'error')  # Changed message to be more generic
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