# admin_category_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
# from models.userModel import User
from App.models.models import User, Prompt, Category, Language
from database import db
from utils import login_required  # Import from utils

admin_language_bp = Blueprint('admin_language_routes', __name__)

# Routes
@admin_language_bp.route('/lanugage')
def language():
    return render_template('/admin/language/language.html')

# Create
@admin_language_bp.route('/api/languages', methods=['POST'])
def create_language():
    data = request.get_json()
    try:
        language = Language(
            code=data['code'],
            name=data['name']
        )
        db.session.add(language)
        db.session.commit()
        return jsonify({'message': 'Language created successfully', 'id': language.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Read all
@admin_language_bp.route('/api/languages', methods=['GET'])
def get_languages():
    languages = Language.query.all()
    return jsonify([{
        'id': lang.id,
        'code': lang.code,
        'name': lang.name,
        'created_at': lang.created_at.isoformat(),
        'updated_at': lang.updated_at.isoformat()
    } for lang in languages])

# Read one
@admin_language_bp.route('/api/languages/<id>', methods=['GET'])
def get_language(id):
    language = Language.query.get_or_404(id)
    return jsonify({
        'id': language.id,
        'code': language.code,
        'name': language.name,
        'created_at': language.created_at.isoformat(),
        'updated_at': language.updated_at.isoformat()
    })

# Update
@admin_language_bp.route('/api/languages/<id>', methods=['PUT'])
def update_language(id):
    language = Language.query.get_or_404(id)
    data = request.get_json()
    try:
        language.code = data['code']
        language.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Language updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Delete
@admin_language_bp.route('/api/languages/<id>', methods=['DELETE'])
def delete_language(id):
    language = Language.query.get_or_404(id)
    try:
        db.session.delete(language)
        db.session.commit()
        return jsonify({'message': 'Language deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400