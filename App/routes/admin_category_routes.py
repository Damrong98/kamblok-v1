# admin_category_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
# from models.userModel import User
from App.models.models import User, Prompt, Category
from database import db
from utils import login_required  # Import from utils

admin_category_bp = Blueprint('admin_category_routes', __name__)

# Routes
@admin_category_bp.route('/category')
def category():
    return render_template('/admin/category/category.html')

# Create
@admin_category_bp.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    try:
        category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Category created successfully', 'id': category.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Read all
@admin_category_bp.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'description': cat.description,
        'created_at': cat.created_at.isoformat(),
        'updated_at': cat.updated_at.isoformat()
    } for cat in categories])

# Read one
@admin_category_bp.route('/api/categories/<id>', methods=['GET'])
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'created_at': category.created_at.isoformat(),
        'updated_at': category.updated_at.isoformat()
    })

# Update
@admin_category_bp.route('/api/categories/<id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get_or_404(id)
    data = request.get_json()
    try:
        category.name = data['name']
        category.description = data.get('description', category.description)
        db.session.commit()
        return jsonify({'message': 'Category updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Delete
@admin_category_bp.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    admin_category_bp.run(debug=True)