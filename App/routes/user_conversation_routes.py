# user_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
# from models.userModel import User
from App.models.models import User, Conversation, Message
from App.database import db
import uuid
from utils import login_required  # Import from utils
from App.functions.gemini_fn import (
    generate_short_title,
    clear_model_chat_history
)

user_conversation_bp = Blueprint('user_conversation_routes', __name__)


"""
Route: Frontend
Return: render_template
"""
# new user chat
@user_conversation_bp.route("/")
@login_required
def user_new_chat():
    clear_model_chat_history()
    return render_template("messages/user_messages.html", conversation_id="", title="New chat")

@user_conversation_bp.route("/chat/<conversation_id>")
@login_required
def user_existed_chat(conversation_id):
    conversation = Conversation.query.get(conversation_id)
    title = conversation.title
    return render_template("messages/user_messages.html", conversation_id=conversation_id, title=title)

"""
Route: API
Return: jsonify
"""  

@user_conversation_bp.route('/api/conversations/<conversation_id>/exists', methods=['GET'])
@login_required
def check_conversation_exists(conversation_id):
    # Query the database for the conversation.
    conversation = Conversation.query.get(conversation_id)
    # Return the result.
    if conversation:
        return jsonify({'exists': True}), 200  # OK
    else:
        return jsonify({'exists': False, 'message': 'Conversation not found'}), 404  # Not Found

# Funtion use:
@user_conversation_bp.route('/api/conversations/create', methods=['POST'])
@login_required
def create_conversation():
    # current_user = User.query.get(session['user_id'])
    auth_id = session.get('user_id')
    # print("user_session_id", auth_id)

    try:
        # Generate a unique conversation ID
        new_slug = str(uuid.uuid4())
        
        # You might want to save this to your database depending on your needs
        # For example:
        new_conversation = Conversation(user_id=auth_id, title="New chat")
        db.session.add(new_conversation)
        db.session.commit()
        
        return jsonify({
            "id": new_conversation.id,
            "status": "success",
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
# Update the title generation in update_conversation_title
# Use Funtion: generate_short_title()
@user_conversation_bp.route('/api/conversations/update_title', methods=['POST'])
@login_required
def update_conversation_title():
    auth_id = session.get('user_id')
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    userPrompt = data.get('userPrompt', '') # New userPrompt to generate the title

    if not conversation_id or not userPrompt:
        return jsonify({"status": "error", "message": "Missing conversation_id or userPrompt"}), 400

    try:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=auth_id).first()
        if not conversation:
            return jsonify({"status": "error", "message": "Conversation not found or unauthorized"}), 404

        new_title = generate_short_title(userPrompt, max_words=5)
        conversation.title = new_title
        db.session.commit()

        return jsonify({
            "status": "success",
            "id": conversation.id,
            "title": new_title
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500 


"""
Route: API
Return: jsonify
"""  
# API Routes
# no use, cau use /api/conversations/pagination
@user_conversation_bp.route('/api/conversations/get_all', methods=['GET'])
@login_required
def get_all_user_converations_api():
    current_user = User.query.get(session['user_id'])

    conversations = Conversation.query.filter_by(user_id=current_user.id).all()
    
    # Convert Conversation objects to a JSON-serializable format
    conversations_data = [
        {
            'id': convo.id,
            'title': convo.title,
            'created_at': convo.created_at.isoformat(),  # Convert datetime to string
            'updated_at': convo.updated_at.isoformat(),
            'user_id': convo.user_id
        } for convo in conversations
    ]
    
    # Return JSON response
    return jsonify({
        'status': 'success',
        'conversations': conversations_data
    })



"""
Route: API
Type: Pagination
Return: jsonify
""" 
# use in layou_api.js
@user_conversation_bp.route('/api/conversations/pagination', methods=['GET'])
@login_required
def get_all_user_converations_pagination_api():
    current_user = User.query.get(session['user_id'])
    
    # Get page parameter from query string, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of conversations per page

    # Query with pagination
    pagination = Conversation.query.filter_by(user_id=current_user.id)\
        .order_by(Conversation.updated_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    conversations = pagination.items
    
    # Convert Conversation objects to a JSON-serializable format
    conversations_data = [
        {
            'id': convo.id,
            'title': convo.title,
            'created_at': convo.created_at.isoformat(),
            'updated_at': convo.updated_at.isoformat(),
            'user_id': convo.user_id
        } for convo in conversations
    ]
    
    return jsonify({
        'status': 'success',
        'conversations': conversations_data,
        'has_more': pagination.has_next,
        'total_pages': pagination.pages,
        'current_page': pagination.page
    })