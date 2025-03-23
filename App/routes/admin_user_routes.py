# admin_user_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
# from models.userModel import User
from App.models.models import User
from App.database import db
from utils import role_required  # Import from utils
from datetime import datetime

admin_user_bp = Blueprint('admin_user_routes', __name__)

# Routes
@admin_user_bp.route('/users', methods=['GET'])
@role_required(1,2)
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = User.query.paginate(page=page, per_page=per_page)
    return render_template('/admin/user/user.html', pagination=pagination)

@admin_user_bp.route('/api/user/create', methods=['POST'])
@role_required(1,2)
def create_user():
    data = request.json
    try:
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data.get('phone_number', ''),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d') if data.get('date_of_birth') else None,
            role=int(data['role']),
            max_messages=int(data.get('max_messages', 0)),
            registration_type=data.get('registration_type', ''),
            is_active=data.get('is_active', True)
        )
        user.set_password(data['password'])
        user.username = user.generate_username()
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return jsonify({'success': True, 'id': user.id})
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating user: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_user_bp.route('/api/user/update/<id>', methods=['POST'])
@role_required(1)
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json
    try:
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.phone_number = data.get('phone_number', user.phone_number)
        user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d') if data.get('date_of_birth') else user.date_of_birth
        user.role = int(data['role'])
        user.max_messages = int(data.get('max_messages', user.max_messages))
        user.registration_type = data.get('registration_type', user.registration_type)
        user.is_active = data.get('is_active', user.is_active)
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        db.session.commit()
        flash('User updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_user_bp.route('/api/user/delete/<id>', methods=['POST'])
@role_required(1)
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400