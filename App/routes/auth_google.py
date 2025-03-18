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

auth_google_bp = Blueprint('auth_google_routes', __name__)


# Google OAuth routes
@auth_google_bp.route('/google/login')
def google_login():
    google = auth_google_bp.google
    redirect_uri = url_for('auth_google_routes.google_callback', _external=True)
    print("Redirect URI sent to Google:", redirect_uri)  # Debug
    return google.authorize_redirect(redirect_uri)

@auth_google_bp.route('/google/callback')
def google_callback():
    google = auth_google_bp.google
    try:
        token = google.authorize_access_token()
        # print("Full Token:", token)  # Debug: Log the entire token
        
        # Parse the ID token without the issuers parameter
        user_info = google.parse_id_token(token, nonce=None)
        # print("User Info:", user_info)  # Debug: Log parsed user info
        # print("Issuer (iss):", user_info.get('iss'))  # Debug: Log the iss claim specifically
        
        # Extract user details
        email = user_info['email']
        first_name = user_info.get('given_name', email.split('@')[0])  # Default to email prefix if no given_name
        last_name = user_info.get('family_name', '')  # Default to empty string if no family_name
        # username = user_info.get('name', email.split('@')[0])  # Use name or email prefix
        picture = user_info.get('picture')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Register new user
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                registration_type="google"  # Explicitly set registration_type
            )
            user.set_password(os.urandom(16).hex())  # Random password for Google users
            db.session.add(user)
            db.session.commit()
            flash('Registration successful via Google!', 'success')

        else:
            # Update fields if missing
            updates = False
            if picture and not user.picture:
                user.picture = picture
                updates = True
            if not user.first_name:
                user.first_name = first_name
                updates = True
            if not user.last_name:
                user.last_name = last_name
                updates = True
            if not user.registration_type:
                user.registration_type = "google"
                updates = True
            if updates:
                db.session.commit()
        
        # Store user data info in session
        session['user_id'] = user.id
        # session['user_role'] = user.role

        print(f"Session set: user_id={session['user_id']}")

        # Update system count for Registration
        SystemSettings.update_registration_count("google")

        flash('Logged in with Google successfully', 'success')
        return redirect(url_for('user_conversation_routes.user_new_chat'))
    
    except OAuthError as e:
        flash(f"OAuth error: {str(e)}", 'error')
        print(f"OAuth Error Details: {str(e)}")  # Debug: Log detailed error
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
        print(f"General Error Details: {str(e)}")  # Debug: Log full error
        return redirect(url_for('auth.login'))
    