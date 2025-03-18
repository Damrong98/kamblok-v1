import os
from flask import Flask, Blueprint, render_template, request, Response, jsonify
from google import genai
import time
from dotenv import load_dotenv
import html  # For basic HTML escaping (a simple form of sanitization)

# Create a Blueprint instance
gemini_api_bp = Blueprint('gemini_api', __name__, static_folder="static", template_folder="templates")

# Initialize environment variables
load_dotenv()

# Configure Google Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Global stop flag and chat history
stop_streaming = False
chat_history = []  # To store user and AI history for frontend
model_chat_history = []  # To store chat history for the model context

def generate_stream(prompt):
    """Generator function to stream AI response with HTML formatting"""
    global stop_streaming
    stop_streaming = False  # Reset flag before streaming

    # Add the user input to the chat history (for frontend)
    # chat_history.append({"role": "user", "content": prompt})

    # Add user input to model's chat history
    model_chat_history.append({"role": "user", "parts":[{"text": prompt}]})
    
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
                    model_chat_history.append({"role": "model", "parts":[{"text": chunk.text}]})
                    
                    yield chunk.text  # Send chunk to frontend
                    time.sleep(0.1)  # Simulate typing effect
        except Exception as e:
            yield f"<p style='color: red;'>Error: {html.escape(str(e))}</p>\n"
    
    return Response(generate(), content_type="text/html")


@gemini_api_bp.route("/chat")
def new_chat():
    global chat_history, model_chat_history
    chat_history=[]
    model_chat_history=[]
    return render_template("gemini_api.html", chat_history=chat_history)

@gemini_api_bp.route("/chat/<name>")
def chat2(name):
    return render_template("gemini_api.html", name=name, chat_history=chat_history)

@gemini_api_bp.route("/stream", methods=["POST"])
def start_chat():
    prompt = request.form["prompt"]
    # check prompt
    return generate_stream(prompt)

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