# admin_category_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
# from models.userModel import User
from App.models.models import User, Prompt, Category
from App.database import db
from utils import login_required, role_required # Import from utils

admin_category_bp = Blueprint('admin_category_routes', __name__)

# Routes
@admin_category_bp.route('/categories', methods=['GET'])
@role_required(1,2)
def categories():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    # pagination = Category.query.paginate(page=page, per_page=per_page)
    pagination = Category.query.order_by(Category.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('/admin/category/category.html', pagination=pagination)

@admin_category_bp.route('/api/category/create', methods=['POST'])
@role_required(1,2)
def create_category():
    data = request.json
    try:
        category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return jsonify({'success': True, 'id': category.id})
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating category: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_category_bp.route('/api/category/update/<id>', methods=['POST'])
@role_required(1)
def update_category(id):
    category = Category.query.get_or_404(id)
    data = request.json
    try:
        category.name = data['name']
        category.description = data.get('description', category.description)
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating category: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_category_bp.route('/api/category/delete/<id>', methods=['POST'])
@role_required(1)
def delete_category(id):
    category = Category.query.get_or_404(id)
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400