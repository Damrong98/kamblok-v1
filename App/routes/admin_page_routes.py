# admin_category_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
# from models.userModel import User
from App.models.models import User, Prompt, Category
from App.models.system_settings import Page
from App.database import db
from utils import role_required # Import from utils

admin_page_bp = Blueprint('admin_page_routes', __name__)



# CRUD
@admin_page_bp.route('/pages', methods=['GET'])
@role_required(1,2)
def pages():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Page.query.order_by(Page.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('/admin/pages/pages.html', pagination=pagination)

@admin_page_bp.route('/api/page/create', methods=['POST'])
@role_required(1,2)
def create_page():
    data = request.json
    try:
        page = Page(
            title=data['title'],
            content=data['content'],
            slug=data['slug'],
            meta_title=data.get('meta_title'),
            meta_description=data.get('meta_description')
        )
        page.save()
        flash('Page created successfully!', 'success')
        return jsonify({'success': True, 'id': page.id})
    except Exception as e:
        flash(f'Error creating page: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_page_bp.route('/api/page/update/<id>', methods=['POST'])
@role_required(1)
def update_page(id):
    data = request.json
    page = Page.query.get_or_404(id)
    try:
        page.title = data['title']
        page.content = data['content']
        page.slug = data['slug']
        page.meta_title = data.get('meta_title')
        page.meta_description = data.get('meta_description')
        page.is_published = data.get('is_published', False)
        db.session.commit()
        flash('Page updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        flash(f'Error updating page: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_page_bp.route('/api/page/delete/<id>', methods=['POST'])
@role_required(1)
def delete_page(id):
    page = Page.query.get_or_404(id)
    try:
        db.session.delete(page)
        db.session.commit()
        flash('Page deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        flash(f'Error deleting page: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400