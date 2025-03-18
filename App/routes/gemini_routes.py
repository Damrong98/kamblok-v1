from flask import Blueprint, render_template, request, Response, jsonify, session
from utils import login_required
from App.models.models import db, User, Conversation, Message, UserMessageLimit
from database import db
from datetime import date, datetime
import uuid
from App.functions.gemini_fn import (
    generate_short_title,
    generate_stream,
    stop_streaming_response,
    clear_chat_history,
    check_chat_history,
    client  # If you need direct access to the client
)

# Create a Blueprint instance
gemini_api_bp = Blueprint('gemini_routes', __name__, static_folder="static", template_folder="templates")

# Global chat history
chat_history = []
model_chat_history = []

# Routes remain largely the same, but use imported functions
@gemini_api_bp.route("/api/ai/get_stream", methods=["POST"])
def start_chat():
    userPrompt = request.form["userPrompt"]
    modelApi = request.form["modelApiName"]
    return Response(generate_stream(userPrompt, modelApi), content_type="text/html")

@gemini_api_bp.route("/api/ai/stop_stream", methods=["POST"])
def stop():
    return jsonify(stop_streaming_response())

# @gemini_api_bp.route("/clear_history", methods=["POST"])
# def clear():
#     return jsonify(clear_chat_history(chat_history, model_chat_history))




"""
User:
Chat
"""

# API endpoint to set chat history
@gemini_api_bp.route('/set_chat_history', methods=['POST'])
def set_chat_history():
    global chat_history
    data = request.get_json()  # Get JSON data from the request
    new_messages = data.get('chat_history', [])
    chat_history.extend(new_messages)  # Append instead of overwrite
    return jsonify({"status": "success", "chat_history": chat_history})

# Optional: Endpoint to retrieve chat history
# @gemini_api_bp.route('/get_chat_history', methods=['GET'])
# def get_chat_history():
#     return jsonify({"chat_history": chat_history})


# Check if chat history is exist
# def check_chat_history(chat_history):
#     if len(chat_history) > 0:
#         # Do something when there is data
#         print("Chat history has data!")
#         print(f"Number of entries: {len(chat_history)}")
#         print("Contents:", chat_history)
#         chat_history=[]
#     else:
#         # Do something when it's empty
#         print("Chat history is empty!")


# @gemini_api_bp.route('api/set_model_chat_history', methods=['POST'])
# def set_model_chat_history_api():
#     global model_chat_history
#     data = request.get_json()  # Get JSON data from the request
#     new_messages = data.get('chat_history', [])
#     model_chat_history(new_messages)  # Append instead of overwrite
#     return jsonify({"status": "success", "model_chat_history": model_chat_history})

