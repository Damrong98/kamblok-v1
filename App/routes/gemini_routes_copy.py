import os
from flask import Flask, Blueprint, render_template, request, Response, jsonify, session
from google import genai
from google.genai import types
import time
from dotenv import load_dotenv
import html  # For basic HTML escaping (a simple form of sanitization)
import uuid
from utils import login_required
# from models.userModel import User
from App.models.models import User, Conversation, Message, UserMessageLimit
from database import db
from datetime import date, datetime

# Create a Blueprint instance
gemini_api_bp = Blueprint('gemini_routes', __name__, static_folder="static", template_folder="templates")

# Initialize environment variables
load_dotenv()

# Configure Google Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Global stop flag and chat history
stop_streaming = False
chat_history = []  # To store user and AI history for frontend
model_chat_history = []  # To store chat history for the model context

print("Model Chat History:", model_chat_history)

def generate_short_title(userPrompt, max_words=5):
    content = f"Generate a concise title (max {max_words} words) for this text: {userPrompt}"
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents= [
                {
                    "role": "user", 
                    "parts":[{"text": content}]
                }
            ],
        )

        # Extract the generated text
        generated_text = response.text.strip()
        # Remove * symbols and extra spaces
        generated_text = generated_text.replace('*', '').replace('  ', ' ').strip()
        
        # Enforce word limit
        words = generated_text.split()
        title = " ".join(words[:min(max_words, len(words))])
        if len(words) > max_words:
            title += "..."  # Plain ellipsis without formatting
        
        return title.capitalize()
    
    except Exception as e:
        print("Error title:", e)
        return "Untitled"

def generate_stream(userPrompt):
    """Generator function to stream AI response with HTML formatting"""
    global stop_streaming
    stop_streaming = False  # Reset flag before streaming

    # Add the user input to the chat history (for frontend)
    # chat_history.append({"role": "user", "content": userPrompt})

    # Add user input to model's chat history
    model_chat_history.append({"role": "user", "parts":[{"text": userPrompt}]})
    
    # Generate the model response based on the entire conversation history
    response = client.models.generate_content_stream(
        # model='gemini-2.0-flash',
        model='gemini-2.0-pro-exp-02-05',
        contents=model_chat_history
    )

    # """this will generate multi role of model ("role": "model")"""
    def generate():
        try:
            for chunk in response:
                if stop_streaming:
                    break  # Stop streaming if flag is set
                if chunk.text:
                    
                    # Add AI's response to frontend chat history
                    # chat_history.append({"role": "model", "content": chunk.text})
                    # Add AI's response to model chat history
                    # model_chat_history.append({"role": "model", "parts":[{"text": chunk.text}]})
                    
                    yield chunk.text  # Send chunk to frontend
                    time.sleep(0.1)  # Simulate typing effect
        except Exception as e:
            yield f"<p style='color: red;'>Error: {html.escape(str(e))}</p>\n"
    
    return Response(generate(), content_type="text/html")


"""
Route: user chat
Return: render_template
"""
# new user chat
@gemini_api_bp.route("/")
@login_required
def user_new_chat():
    return render_template("messages/user_messages.html", conversation_id="")

@gemini_api_bp.route("/chat/<conversation_id>")
@login_required
def user_existed_chat(conversation_id):
    return render_template("messages/user_messages.html", conversation_id=conversation_id)



"""
User:
Chat
"""
# @gemini_api_bp.route("/chat")
# @login_required
# def new_chat():
#     global chat_history, model_chat_history
#     chat_history=[]
#     model_chat_history=[]
#     current_user = User.query.get(session['user_id'])
#     return render_template("gemini_api.html", chat_history=chat_history, current_user=current_user)

# @gemini_api_bp.route("/chat/<name>")
# @login_required
# def chat2(name):
#     current_user = User.query.get(session['user_id'])
#     return render_template("gemini_api.html", name=name, chat_history=chat_history, current_user=current_user)

@gemini_api_bp.route("/stream", methods=["POST"])
def start_chat():
    userPrompt = request.form["userPrompt"]
    # check userPrompt
    return generate_stream(userPrompt)

@gemini_api_bp.route("/stop", methods=["POST"])
def stop():
    """Stop the streaming process"""
    global stop_streaming
    stop_streaming = True
    return jsonify({"status": "stopped"})

@gemini_api_bp.route("/clear_history", methods=["POST"])
def clear():
    """Clear all chat history"""
    global chat_history, model_chat_history
    chat_history = []  # To clear user and AI history 
    model_chat_history = []  # To clear chat history
    return jsonify({"status": "Your chat history was clear!"})

# API endpoint to set chat history
@gemini_api_bp.route('/set_chat_history', methods=['POST'])
def set_chat_history():
    global chat_history
    data = request.get_json()  # Get JSON data from the request
    new_messages = data.get('chat_history', [])
    chat_history.extend(new_messages)  # Append instead of overwrite
    return jsonify({"status": "success", "chat_history": chat_history})

# Optional: Endpoint to retrieve chat history
@gemini_api_bp.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    return jsonify({"chat_history": chat_history})

# Check if chat history is exist
def check_chat_history(chat_history):
    if len(chat_history) > 0:
        # Do something when there is data
        print("Chat history has data!")
        print(f"Number of entries: {len(chat_history)}")
        print("Contents:", chat_history)
        chat_history=[]
    else:
        # Do something when it's empty
        print("Chat history is empty!")


@gemini_api_bp.route('api/set_model_chat_history', methods=['POST'])
def set_model_chat_history_api():
    global model_chat_history
    data = request.get_json()  # Get JSON data from the request
    new_messages = data.get('chat_history', [])
    model_chat_history(new_messages)  # Append instead of overwrite
    return jsonify({"status": "success", "model_chat_history": model_chat_history})



"""
User: 
Return: jsonify
"""

@gemini_api_bp.route("/api/get_messages/<conversation_id>")
@login_required
def get_messages_by_conversationID(conversation_id):
    global model_chat_history

    # clear chat history
    chat_history = []
    model_chat_history = []

    current_user = User.query.get(session['user_id'])
    
    # Verify the conversation belongs to the current user
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
    if not conversation:
        return jsonify({'status': 'error', 'message': 'Conversation not found or not authorized'}), 404
    
    # Get all messages for the conversation
    messages = Message.query.filter_by(conversation_id=conversation_id).all()
    
    # Convert messages to JSON-serializable format
    messages_data = [
        {
            'id': msg.id,
            'sender': msg.sender,
            'message_text': msg.message_text,
            'message_html': msg.message_html,
            'timestamp': msg.timestamp.isoformat(),
            'api_response_time': msg.api_response_time
        } for msg in messages
    ]

    model_chat_history=[
        {
            "role": msg.sender,  # 'user' or 'model'
            "parts":[{"text": msg.message_text}]
        } for msg in messages
    ]

    print("get_messages_by_conversationID (model_chat_history):", model_chat_history)

    return jsonify({
        'status': 'success',
        'messages': messages_data,
        'chat_history': chat_history,
        'current_user': {
            'id': current_user.id,
            'username': current_user.username  # Add any other user fields you need
        }
    })


@gemini_api_bp.route('/api/create_conversation', methods=['POST'])
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
    
@gemini_api_bp.route('/api/update_conversation_title', methods=['POST'])
def update_conversation_title():
    auth_id = session.get('user_id')

    # Get data from the request
    data = request.get_json()
    conversation_id = data.get('conversation_id')  # UUID or DB ID, depending on your setup
    # conversation_id = int(str_conversation_id)

    userPrompt = data.get('userPrompt', '')  # New userPrompt to generate the title

    print("Promt:", userPrompt, conversation_id)

    if not conversation_id or not userPrompt:
        return jsonify({"status": "error", "message": "Missing conversation_id or userPrompt"}), 400

    try:
        # Find the conversation (assuming conversation_id is the UUID; adjust if using DB id)
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=auth_id).first()
        
        if not conversation:
            return jsonify({"status": "error", "message": "Conversation not found or unauthorized"}), 404

        # Generate new title based on the userPrompt
        new_title = generate_short_title(userPrompt, max_words=5)
        print("Title:", new_title)

        conversation.title = new_title

        # Commit the update to the database
        db.session.commit()

        return jsonify({
            "status": "success",
            "id": conversation.id,
            "title": new_title
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    



# Create a message
# Udate Chat History (chat_history, model_chat_history)
@gemini_api_bp.route('/api/send_message', methods=['POST'])
def send_message():
    global chat_history, model_chat_history

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
        
        # Add to chat_history and database
        # chat_history.extend(new_messages)
        # chat_history.append({"role": new_message.sender, "content": new_message.message_text})
        model_chat_history.append({"role": new_message.sender, "parts":[{"text": new_message.message_text}]})
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "chat_history": chat_history
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
    