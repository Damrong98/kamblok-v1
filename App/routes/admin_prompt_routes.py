# admin_prompt_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
# from models.userModel import User
from App.models.models import User, Prompt, Category, Language
from App.database import db
from utils import role_required  # Import from utils

admin_prompt_bp = Blueprint('admin_prompt_routes', __name__)

# Routes
@admin_prompt_bp.route('/prompts', methods=['GET'])
@role_required(1,2)
def prompts():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Prompt.query.order_by(Prompt.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('/admin/prompt/prompt.html', pagination=pagination)

@admin_prompt_bp.route('/api/prompt/create', methods=['POST'])
@role_required(1,2)
def create_prompt():
    data = request.json
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
        flash('Prompt created successfully!', 'success')
        return jsonify({'success': True, 'id': prompt.id})
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating prompt: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_prompt_bp.route('/api/prompt/update/<id>', methods=['POST'])
@role_required(1)
def update_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    data = request.json
    try:
        prompt.prompt_text = data['prompt_text']
        prompt.category_id = data['category_id'] or None
        prompt.language_id = data['language_id'] or None
        prompt.is_active = data.get('is_active', False)
        db.session.commit()
        flash('Prompt updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating prompt: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_prompt_bp.route('/api/prompt/delete/<id>', methods=['POST'])
@role_required(1)
def delete_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    try:
        db.session.delete(prompt)
        db.session.commit()
        flash('Prompt deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting prompt: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_prompt_bp.route('/api/categories', methods=['GET'])
@role_required(1,2)
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@admin_prompt_bp.route('/api/languages', methods=['GET'])
@role_required(1,2)
def get_languages():
    languages = Language.query.all()
    return jsonify([{'id': l.id, 'name': l.name} for l in languages])