import os
from google import genai
import html
import time
from dotenv import load_dotenv
from App.models.system_settings import SystemSettings

# Initialize environment variables
load_dotenv()


# Function to get the API key from SystemSettings
# def get_model_api_key():
#     try:
#         # Query the SystemSettings table (assuming there's at least one row)
#         settings = SystemSettings.query.first()  # Get the first record
#         if settings and settings.model_api_key:
#             return settings.model_api_key
#         else:
#             # Fallback to environment variable if no key is found in DB
#             return os.getenv("GEMINI_API_KEY", "default")
#     except Exception as e:
#         print(f"Error retrieving API key from database: {e}")
#         return os.getenv("GEMINI_API_KEY", "default")
    
# # Configure Google Gemini API with the key from SystemSettings
# client = genai.Client(api_key=get_model_api_key())

# Configure Google Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# Global stop flag
stop_streaming = False
model_chat_history = []

def generate_short_title(userPrompt, max_words=5):
    """Generate a concise title based on user prompt"""
    content = f"Generate a concise title (max {max_words} words) for this text: {userPrompt}"
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                {
                    "role": "user", 
                    "parts":[{"text": content}]
                }
            ],
        )

        # Extract and clean the generated text
        generated_text = response.text.strip()
        generated_text = generated_text.replace('*', '').replace('  ', ' ').strip()
        
        # Enforce word limit
        words = generated_text.split()
        title = " ".join(words[:min(max_words, len(words))])
        if len(words) > max_words:
            title += "..."
        
        return title.capitalize()
    
    except Exception as e:
        print("Error generating title:", e)
        return "Untitled"
    
def generate_stream(userPrompt, modelApi):
    """Generator function to stream AI response with HTML formatting"""
    global stop_streaming
    stop_streaming = False

    # Add user input to model's chat history
    model_chat_history.append({"role": "user", "parts":[{"text": userPrompt}]})
    
    # Generate the model response
    response = client.models.generate_content_stream(
        model=modelApi,
        contents=model_chat_history

    )

    def generate():
        try:
            for chunk in response:
                if stop_streaming:
                    break
                if chunk.text:
                    yield chunk.text
                    # Add AI's response to model chat history
                    model_chat_history.append({"role": "model", "parts":[{"text": chunk.text}]})
                    time.sleep(0.1)  # Simulate typing effect
        except Exception as e:
            yield f"<p style='color: red;'>Error: {html.escape(str(e))}</p>\n"
    
    return generate()


"""Function"""
def set_model_chat_history(messages):
    global model_chat_history
    model_chat_history=[
        {
            "role": msg.sender,  # 'user' or 'model'
            "parts":[{"text": msg.message_text}]
        } for msg in messages
    ]
    # print("set_model_chat_history", model_chat_history)
    return True

def clear_model_chat_history():
    global model_chat_history
    model_chat_history = []
    # print("set_model_chat_history", model_chat_history)
    return True

# 
# def update_model_chat_history(role, text):
#     """Update the model_chat_history with a new message"""
#     global model_chat_history
#     model_chat_history.append({
#         "role": role,
#         "parts": [{"text": text}]
#     })

# def get_model_chat_history():
#     """Return the current model_chat_history"""
#     global model_chat_history
#     return model_chat_history

# 
def stop_streaming_response():
    """Stop the streaming process"""
    global stop_streaming
    stop_streaming = True
    return {"status": "stopped"}

def clear_chat_history(chat_history, model_chat_history):
    """Clear all chat history"""
    chat_history.clear()
    model_chat_history.clear()
    return {"status": "Your chat history was cleared!"}

def check_chat_history(chat_history):
    """Check if chat history exists and print status"""
    if len(chat_history) > 0:
        print("Chat history has data!")
        print(f"Number of entries: {len(chat_history)}")
        print("Contents:", chat_history)
        return True
    else:
        print("Chat history is empty!")
        return False