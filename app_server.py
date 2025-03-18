# app.py
from flask import Flask, render_template, session, jsonify
import os
from database import db, init_db
from oauth_config import init_oauth
from utils import login_required, role_required

from App.routes.auth import auth_bp
from App.routes.admin_user_routes import admin_user_bp
from App.routes.user_conversation_routes import user_conversation_bp
from App.routes.message_routes import message_bp
from App.routes.gemini_routes import gemini_api_bp
from App.routes.user_message_limit_routes import user_message_limit_bp
from App.routes.prompt_routes import user_prompt_bp


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SECRET_KEY'] = os.urandom(24).hex()

# # Google OAuth configuration
# app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID")
# app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET")


# Initialize database
init_db(app)

# Initialize OAuth
google = init_oauth(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_user_bp, url_prefix="/admin")
app.register_blueprint(gemini_api_bp, url_prefix="")
app.register_blueprint(user_conversation_bp)
app.register_blueprint(message_bp)
app.register_blueprint(user_message_limit_bp)
app.register_blueprint(user_prompt_bp)

@app.route('/home')
def home():
    # user_id = session.get('user_id')
    return render_template("index.html")

@app.route('/admin')
@login_required
@role_required(1)
def admin():
    return render_template("admin/index.html")


# Route for chat data
@app.route('/get_chat_data')
def get_chat_data():
    return jsonify(message="Chat data loaded successfully!")

# Route for profile data
@app.route('/get_profile_data')
def get_profile_data():
    return jsonify(message="Profile data loaded successfully!")

# Route for dashboard data
@app.route('/get_dashboard_data')
def get_dashboard_data():
    return jsonify(message="Dashboard data loaded successfully!")

# Provide google to auth blueprint (optional, if needed)
auth_bp.google = google  # Attach google to the blueprint for use in routes

if __name__ == '__main__':
    app.run(debug=True)