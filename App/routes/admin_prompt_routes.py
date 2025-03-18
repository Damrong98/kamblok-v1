# admin_prompt_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
# from models.userModel import User
from App.models.models import User, Prompt, Category, Language
from database import db
from utils import login_required  # Import from utils

admin_prompt_bp = Blueprint('admin_prompt_routes', __name__)

# Routes
@admin_prompt_bp.route('/prompt')
def prompt():
    return render_template('/admin/prompt/prompt.html')

# Create
@admin_prompt_bp.route('/api/prompts', methods=['POST'])
def create_prompt():
    data = request.get_json()
    current_user = User.query.get(session['user_id'])
    try:
        prompt = Prompt(
            user_id=current_user.id,
            prompt_text=data['prompt_text'],
            category_id=data['category_id'] or None,
            language_id=data['language_id'] or None,
            is_active=data.get('is_active', True)
        )
        db.session.add(prompt)
        db.session.commit()
        return jsonify({'message': 'Prompt created successfully', 'id': prompt.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Read all
@admin_prompt_bp.route('/api/prompts', methods=['GET'])
def get_prompts():
    prompts = Prompt.query.all()
    return jsonify([{
        'id': p.id,
        'user_id': p.user_id,
        'user_name': f"{p.user.first_name} {p.user.last_name}" if p.user else 'Unknown',
        'prompt_text': p.prompt_text,
        'category_id': p.category_id,
        'category_name': p.category.name if p.category else None,
        'language_id': p.language_id,
        'language_name': p.language.name if p.language else None,
        'is_active': p.is_active,
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat()
    } for p in prompts])

# Read one
@admin_prompt_bp.route('/api/prompts/<id>', methods=['GET'])
def get_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    return jsonify({
        'id': prompt.id,
        'user_id': prompt.user_id,
        'prompt_text': prompt.prompt_text,
        'category_id': prompt.category_id,
        'language_id': prompt.language_id,
        'is_active': prompt.is_active,
        'created_at': prompt.created_at.isoformat(),
        'updated_at': prompt.updated_at.isoformat()
    })

# Update
@admin_prompt_bp.route('/api/prompts/<id>', methods=['PUT'])
def update_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    data = request.get_json()
    current_user = User.query.get(session['user_id'])
    try:
        prompt.user_id = current_user.id
        prompt.prompt_text = data['prompt_text']
        prompt.category_id = data['category_id'] or None
        prompt.language_id = data['language_id'] or None
        prompt.is_active = data.get('is_active', prompt.is_active)
        db.session.commit()
        return jsonify({'message': 'Prompt updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Delete
@admin_prompt_bp.route('/api/prompts/<id>', methods=['DELETE'])
def delete_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    try:
        db.session.delete(prompt)
        db.session.commit()
        return jsonify({'message': 'Prompt deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Get categories for dropdown
@admin_prompt_bp.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

# Get languages for dropdown
@admin_prompt_bp.route('/api/languages', methods=['GET'])
def get_languages():
    languages = Language.query.all()
    return jsonify([{'id': l.id, 'name': l.name} for l in languages])

# Get users for dropdown
@admin_prompt_bp.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'name': f"{u.first_name} {u.last_name}"
    } for u in users])