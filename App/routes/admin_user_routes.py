# admin_user_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
# from models.userModel import User
from App.models.models import User
from database import db
from utils import login_required  # Import from utils
from datetime import datetime

admin_user_bp = Blueprint('admin_user_routes', __name__)

# Routes
@admin_user_bp.route('/user')
def user():
    return render_template('/admin/user/user.html')

# Create
@admin_user_bp.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d') if data.get('date_of_birth') else None,
            role=int(data['role']),
            max_messages=int(data.get('max_messages', 0)),
            registration_type=data.get('registration_type'),
            is_active=data.get('is_active', True)
        )
        user.set_password(data['password'])
        user.username = user.generate_username()
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Read all
@admin_user_bp.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'username': u.username,
        'date_of_birth': u.date_of_birth.isoformat() if u.date_of_birth else None,
        'phone_number': u.phone_number,
        'email': u.email,
        'role': u.role,
        'role_name': u.get_role_name(),
        'max_messages': u.max_messages,
        'registration_type': u.registration_type,
        'last_login': u.last_login.isoformat() if u.last_login else None,
        'is_active': u.is_active,
        'created_at': u.created_at.isoformat(),
        'updated_at': u.updated_at.isoformat()
    } for u in users])

# Read one
@admin_user_bp.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'phone_number': user.phone_number,
        'email': user.email,
        'role': user.role,
        'max_messages': user.max_messages,
        'registration_type': user.registration_type,
        'is_active': user.is_active
    })

# Update
@admin_user_bp.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    try:
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.phone_number = data.get('phone_number')
        user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d') if data.get('date_of_birth') else None
        user.role = int(data['role'])
        user.max_messages = int(data.get('max_messages', user.max_messages))
        user.registration_type = data.get('registration_type')
        user.is_active = data.get('is_active', user.is_active)
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Delete
@admin_user_bp.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400