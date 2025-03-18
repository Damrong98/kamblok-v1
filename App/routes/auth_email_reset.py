from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, session
from App.models.models import User 
from database import db
from flask_mail import Message
import random
from datetime import datetime, timedelta
import base64

auth_email_reset_bp = Blueprint('auth_email_reset', __name__)

# Temporary storage for pending email verifications
pending_verifications = {}

# Temporary storage for reset codes
reset_verifications = {}

def generate_verification_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

# Route for the initial register page
@auth_email_reset_bp.route('/forget_password', methods=['GET'])
def forget_password_page():
    return render_template('/auth/forget_password.html')


# Route to initiate forgot password
@auth_email_reset_bp.route('/forgot-password/start', methods=['POST'])
def start_forgot_password():
    data = request.get_json()
    email = data.get('email') if data else None

    if not email or not isinstance(email, str) or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not registered'}), 404

    # Generate and store reset code (reuse existing function)
    code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=1)
    reset_verifications[email] = {
        'email': email,
        'code': code,
        'expires_at': expires_at
    }

    msg = Message('Reset Your Password', recipients=[email])
    msg.body = f'Your password reset code is: {code}\nThis code will expire in 1 minute.'
    try:
        current_app.mail.send(msg)
        return jsonify({'message': 'Reset code sent to your email'}), 200
    except Exception as e:
        del reset_verifications[email]
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

# Route to serve verify password page
@auth_email_reset_bp.route('/verify-password', methods=['GET'])
def verify_password_page():
    return render_template('/auth/verify_password.html')

# API to send or resend reset code
@auth_email_reset_bp.route('/api/send-reset-code', methods=['GET'])
def send_reset_code():
    email = request.args.get('email')
    
    if not email or not isinstance(email, str) or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    
    reg_data = reset_verifications.get(email)
    if not reg_data:
        return jsonify({'error': 'No reset in progress. Please start over.'}), 403

    resend = request.args.get('resend', 'false').lower() == 'true'
    current_time = datetime.now()
    should_generate_new_code = (
        'code' not in reg_data or 
        resend or 
        (reg_data.get('expires_at') and current_time >= reg_data['expires_at'])
    )

    if should_generate_new_code:
        code = generate_verification_code()
        expires_at = current_time + timedelta(minutes=2)
        reset_verifications[email] = {
            'email': email,
            'code': code,
            'expires_at': expires_at
        }

        msg = Message('Reset Your Password', recipients=[email])
        msg.body = f'Your password reset code is: {code}\nThis code will expire in 1 minute.'
        try:
            current_app.mail.send(msg)
            return jsonify({
                'message': 'Reset code sent to your email',
                'expires_in': 120
            }), 200
        except Exception as e:
            if 'code' not in reg_data or resend:
                del reset_verifications[email]
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

    expires_in = int((reg_data['expires_at'] - current_time).total_seconds())
    if expires_in > 0:
        return jsonify({
            'message': 'Reset code already sent',
            'expires_in': expires_in
        }), 200
    else:
        return jsonify({
            'message': 'Reset code has expired. Please resend.',
            'expires_in': 0
        }), 200

# API to verify reset code
@auth_email_reset_bp.route('/api/verify-reset-code', methods=['POST'])
def verify_reset_code():
    data = request.get_json()
    email = data.get('email') if data else None
    reset_code = data.get('reset_code') if data else None

    if not email or email not in reset_verifications:
        return jsonify({'error': 'No reset in progress'}), 404

    reg_data = reset_verifications[email]
    
    if datetime.now() >= reg_data['expires_at']:
        return jsonify({'error': 'Reset code expired'}), 410

    if reg_data['code'] == reset_code:
        return jsonify({'message': 'Code verified successfully'}), 200
    
    return jsonify({'error': 'Invalid reset code'}), 400

# API to reset password
@auth_email_reset_bp.route('/api/reset-password', methods=['POST'])
def reset_password_api():
    data = request.get_json()
    email = data.get('email') if data else None
    new_password = data.get('new_password') if data else None

    if not email or email not in reset_verifications:
        return jsonify({'error': 'Verification not completed or expired'}), 403

    if not new_password:
        return jsonify({'error': 'New password is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.set_password(new_password)
    db.session.commit()
    
    del reset_verifications[email]  # Clean up
    login_url = url_for('auth.login', _external=True)
    return jsonify({
        'message': 'Password reset successful! Redirecting to login...',
        'redirect': login_url
    }), 200