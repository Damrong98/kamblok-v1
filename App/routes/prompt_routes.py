# user_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
# from models.userModel import User
from App.models.models import User, Prompt, Category, Language
from App.database import db
from utils import login_required  # Import from utils

user_prompt_bp = Blueprint('user_prompt_routes', __name__)


@user_prompt_bp.route('/prompts', methods=['GET'])
@login_required
def get_all_prompts():
    return render_template('prompts/show_prompts.html')

@user_prompt_bp.route('/api/prompts', methods=['GET'])
@login_required
def get_prompts_by_language_and_category():
    """
    API endpoint to fetch prompts with optional filters and pagination (10 items per page).
    
    Query Parameters:
        all (bool): If true, fetch all prompts without any filters (optional)
        language_id (str): The ID of the language (optional unless all=false)
        category_id (str): The ID of the category (optional unless all=false)
        page (int): Page number (optional, defaults to 1)
        is_active (bool): Filter by active status (optional, defaults to True, ignored if all=true)
    
    Returns:
        JSON response with paginated list of prompts and metadata
    """
    try:
        # Get query parameters
        fetch_all = request.args.get('all', default='false', type=lambda v: v.lower() == 'true')
        print("FETHALL", fetch_all)

        # Get language_id from query parameters, if provided
        language_id = request.args.get('language_id')
   
        # If no language_id is provided, use the default language's ID
        if not fetch_all and not language_id:
            default_language = Language.query.filter_by(status='default').first()
            language_id = default_language.id if default_language else None

        print("LanugageId", language_id)
        category_id = request.args.get('category_id')
        page = request.args.get('page', default=1, type=int)
        is_active = request.args.get('is_active', default='true', type=lambda v: v.lower() == 'true')

        # Set pagination constants
        LIMIT = 10
        offset = (page - 1) * LIMIT

        # Build the query
        if fetch_all:
            query = Prompt.query
        if language_id:
            query = query.filter(Prompt.language_id == language_id)
        if category_id:
            query = query.filter(Prompt.category_id == category_id)
        if category_id and language_id:
            query = query.filter(
                Prompt.category_id == category_id, Prompt.language_id == language_id
            )

        # Get total count before pagination
        total = query.count()
        
        # Calculate total pages
        total_pages = (total + LIMIT - 1) // LIMIT
        
        # Apply pagination
        prompts = query.order_by(Prompt.created_at.desc())\
                      .limit(LIMIT)\
                      .offset(offset)\
                      .all()

        # Format response data
        prompts_data = [{
            'id': prompt.id,
            'user_id': prompt.user_id,
            'prompt_text': prompt.prompt_text,
            'category_id': prompt.category_id,
            'category_name': prompt.category.name if prompt.category else None,
            'language_id': prompt.language_id,
            'language_name': prompt.language.name if prompt.language else None,
            'created_at': prompt.created_at.isoformat(),
            'is_active': prompt.is_active
        } for prompt in prompts]

        # Return response
        return jsonify({
            'status': 'success',
            'data': prompts_data,
            'metadata': {
                'total': total,
                'per_page': LIMIT,
                'current_page': page,
                'total_pages': total_pages,
                'returned': len(prompts_data),
                'has_next': page < total_pages,
                'has_previous': page > 1
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'An error occurred while processing your request',
            'message': str(e)
        }), 500
    

@user_prompt_bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@user_prompt_bp.route('/api/languages', methods=['GET'])
@login_required
def get_languages():
    languages = Language.query.all()
    return jsonify([{'id': l.id, 'name': l.name, 'status': l.status} for l in languages])