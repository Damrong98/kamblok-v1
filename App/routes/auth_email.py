from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, session
from App.models.models import User 
from App.models.system_settings import SystemSettings
from App.database import db
from flask_mail import Message
import random
from datetime import datetime, timedelta
import base64

auth_email_bp = Blueprint('auth_email', __name__)

# Temporary storage for pending email verifications
pending_verifications = {}

def generate_verification_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


# Route for the registration page with obfuscated email
@auth_email_bp.route('/registration', methods=['GET'])
def registration_page():
    encoded_email = request.args.get('email')
    if encoded_email:
        try:
            # Add padding if needed (Base64 strings must be multiple of 4 in length)
            padding_needed = (4 - len(encoded_email) % 4) % 4
            padded_encoded_email = encoded_email + ('=' * padding_needed)
            # Decode standard Base64
            email = base64.b64decode(padded_encoded_email.encode()).decode('utf-8')
            session['registration_email'] = email  # Store in session for later use
        except Exception as e:
            return jsonify({'error': f'Invalid email parameter: {str(e)}'}), 400
    return render_template('/auth/registration.html')

# Step 1: Collect email
@auth_email_bp.route('/api/register-email', methods=['POST'])
def register_email_api():
    data = request.get_json()
    email = data.get('email') if data else None

    if not email or not isinstance(email, str) or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Store email in pending_verifications
    pending_verifications[email] = {'email': email}
    return jsonify({
        'message': 'Email registered successfully',
        'redirect': '/registration#step2'
    }), 201


# Step 2: Send verification code
@auth_email_bp.route('/api/send-verification-code', methods=['GET'])
def send_verification_code():
    email = request.args.get('email')
    
    if not email or not isinstance(email, str) or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    
    reg_data = pending_verifications.get(email)
    if not reg_data:
        return jsonify({'error': 'No registration in progress. Please start over.'}), 403

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
        pending_verifications[email] = {
            'email': email,
            'code': code,
            'expires_at': expires_at
        }

        msg = Message('Verify Your Email', recipients=[email])
        # msg.body = f'Your verification code is: {code}\nThis code will expire in 2 minute.'
        msg.html = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #f9f9f9;
                        border-radius: 8px;
                        padding: 30px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .logo {{
                        text-align: center;
                        margin-bottom: 20px;
                        font-size: 28px;
                        font-weight: bold;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                    }}
                    h2 {{
                        color: #2c3e50;
                        margin-top: 0;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }}
                    .code-box {{
                        background-color: #ffffff;
                        border: 2px solid #3498db;
                        border-radius: 4px;
                        padding: 15px;
                        text-align: center;
                        margin: 20px 0;
                        font-size: 24px;
                        font-weight: bold;
                        color: #2c3e50;
                    }}
                    .footer {{
                        font-size: 12px;
                        color: #666666;
                        margin-top: 20px;
                        padding-top: 10px;
                        border-top: 1px solid #eeeeee;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="logo">Kamblok</div>
                    <h2>Email Verification</h2>
                    <p>Hello,</p>
                    <p>Please use the following verification code to complete your email verification:</p>
                    <div class="code-box">{code}</div>
                    <p>This code will expire in 2 minutes. If you didn't request this verification, 
                       please disregard this email.</p>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply directly to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        try:
            current_app.mail.send(msg)
            return jsonify({
                'message': 'Verification code sent to your email',
                'expires_in': 120
            }), 200
        except Exception as e:
            if 'code' not in reg_data or resend:
                del pending_verifications[email]
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

    expires_in = int((reg_data['expires_at'] - current_time).total_seconds())
    if expires_in > 0:
        return jsonify({
            'message': 'Verification code already sent',
            'expires_in': expires_in
        }), 200
    else:
        return jsonify({
            'message': 'Verification code has expired. Please resend.',
            'expires_in': 0
        }), 200

# Step 2: Verify code
@auth_email_bp.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('email') if data else None
    email_code = data.get('email_code') if data else None

    if not email or email not in pending_verifications:
        return jsonify({'error': 'No verification in progress'}), 404

    reg_data = pending_verifications[email]
    
    if datetime.now() >= reg_data['expires_at']:
        return jsonify({'error': 'Verification code expired'}), 410

    if reg_data['code'] == email_code:
        return jsonify({
            'message': 'Verification successful',
            'redirect': '/registration#step3'
        }), 200
    
    return jsonify({'error': 'Invalid verification code'}), 400

# Step 3: Complete registration
@auth_email_bp.route('/api/complete-registration', methods=['POST'])
def complete_registration_api():
    data = request.get_json()
    email = data.get('email') if data else None
    
    if not email or email not in pending_verifications:
        return jsonify({'error': 'Verification not completed or expired'}), 403

    reg_data = pending_verifications[email]
    
    first_name = data.get('first_name') if data else None
    last_name = data.get('last_name') if data else None
    password = data.get('password') if data else None
    confirm_password = data.get('confirm_password') if data else None

    if not all([first_name, last_name, password, confirm_password]):
        return jsonify({'error': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    user = User(
        username=None,
        first_name=first_name,
        last_name=last_name,
        email=email,
        registration_type="email"  # Explicitly set registration_type
    )
    user.set_password(password)
    user.email_verification_code = reg_data['code']
    
    db.session.add(user)
    db.session.commit()

    # Update system count for Registration
    SystemSettings.update_registration_count("email")
    
    del pending_verifications[email]  # Clean up pending verification
    login_url = url_for('auth.login', _external=True)
    return jsonify({
        'message': 'Registration successful! Redirecting to login...',
        'redirect': login_url
    }), 201
