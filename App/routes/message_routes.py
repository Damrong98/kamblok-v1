from flask import Blueprint, render_template, request, Response, jsonify, session
from utils import login_required
from App.models.models import User, Conversation, Message, UserMessageLimit
from database import db
from datetime import date, datetime
import uuid
from App.functions.gemini_fn import (
    set_model_chat_history,
    clear_model_chat_history
)

# Create a Blueprint instance
message_bp = Blueprint('message_routes', __name__, static_folder="static", template_folder="templates")

"""
User: 
Return: jsonify
"""

# use in user_message.js
@message_bp.route("/api/messages/get_all/<conversation_id>")
@login_required
def get_messages_by_conversationID(conversation_id):
    """
    Fetch messages from a conversation with pagination
    Expects optional query params: 'offset' and 'limit'
    """
    clear_model_chat_history()
    current_user = User.query.get(session['user_id'])
    
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
    if not conversation:
        return jsonify({'status': 'error', 'message': 'Conversation not found or not authorized'}), 404
    
    # Get pagination parameters from query string
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=10, type=int)
    
    # Get messages with pagination
    messages = Message.query.filter_by(conversation_id=conversation_id)\
                           .order_by(Message.created_at.desc())\
                           .offset(offset)\
                           .limit(limit)\
                           .all()
    
    messages_data = [
        {
            'id': msg.id,
            'sender': msg.sender,
            'message_text': msg.message_text,
            'message_html': msg.message_html,
            'created_at': msg.created_at.isoformat(),
            'api_response_time': msg.api_response_time
        } for msg in messages
    ]

    set_model_chat_history(messages)
    
    return jsonify({
        'status': 'success',
        'messages': messages_data,
        'current_user': {
            'id': current_user.id,
            'username': current_user.username
        },
        'has_more': len(messages) == limit  # Indicate if there are more messages to load
    })


# Create a message
# Udate Chat History (chat_history, model_chat_history)
# use in user_message.js
@message_bp.route('/api/messages/send', methods=['POST'])
def send_message():
    """
    Create a new message and update chat history
    Expects JSON data with 'chat_history' containing message details
    Use Function: update_model_chat_history() from App.function.gemini_fn.py
    """

    auth_id = session.get('user_id')

    try:
        data = request.get_json()
        
        # Check if data exists and has chat_history
        if not data or 'chat_history' not in data:
            return jsonify({"status": "error", "message": "No chat_history provided"}), 400
            
        new_messages = data.get('chat_history', [])
        
        # Assuming new_messages is a list of message objects
        if not new_messages or not isinstance(new_messages, list):
            return jsonify({"status": "error", "message": "Invalid chat_history format"}), 400
            
        # Process first message (assuming we're saving one at a time since frontend sends array with one item)
        message_data = new_messages[0]
        
        new_message = Message(
            conversation_id=message_data.get('conversionID'),  # Fixed typo from 'conversionID'
            sender=message_data.get('sender'),
            message_text=message_data.get('fullResponseText'),
            message_html=message_data.get('fullResponseText'),
            # api_response_time=0.8  # Uncomment and modify if needed
        )
        
        print("Message:", new_message)
        
        # # Update model_chat_history using utility function
        # update_model_chat_history(new_message.sender, new_message.message_text)
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            # "chat_history": chat_history
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
    