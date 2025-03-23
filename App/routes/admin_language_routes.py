# admin_category_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
# from models.userModel import User
from App.models.models import User, Prompt, Category, Language
from App.database import db
from utils import role_required # Import from utils

admin_language_bp = Blueprint('admin_language_routes', __name__)

# Routes
@admin_language_bp.route('/languages', methods=['GET'])
@role_required(1,2)
def languages():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Language.query.order_by(Language.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('/admin/language/language.html', pagination=pagination)

@admin_language_bp.route('/api/language/create', methods=['POST'])
@role_required(1,2)
def create_language():
    data = request.json
    try:
        language = Language(
            code=data['code'],
            name=data['name']
        )
        db.session.add(language)
        db.session.commit()
        flash('Language created successfully!', 'success')
        return jsonify({'success': True, 'id': language.id})
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating language: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_language_bp.route('/api/language/update/<id>', methods=['POST'])
@role_required(1)
def update_language(id):
    language = Language.query.get_or_404(id)
    data = request.json
    try:
        language.code = data['code']
        language.name = data['name']
        db.session.commit()
        flash('Language updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating language: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_language_bp.route('/api/language/delete/<id>', methods=['POST'])
@role_required(1)
def delete_language(id):
    language = Language.query.get_or_404(id)
    try:
        if language.status == 'default':
            flash('Cannot delete default language!', 'danger')
            return jsonify({'success': False, 'error': 'Cannot delete default language'}), 400
        db.session.delete(language)
        db.session.commit()
        flash('Language deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting language: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_language_bp.route('/api/language/set-default/<id>', methods=['POST'])
@role_required(1)
def set_default_language(id):
    language = Language.query.get_or_404(id)
    try:
        language.set_as_default()
        flash('Language set as default successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error setting default language: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400