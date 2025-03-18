# app.py
from flask import Flask, render_template, session, jsonify
import os
from database import db, init_db
from oauth_config import init_oauth
from utils import login_required, role_required
from flask_mail import Mail
from config import Config
from flask_migrate import Migrate
# 
from App.models.system_settings import SystemSettings

# from App.models import db
from App.routes.auth import auth_bp
from App.routes.auth_email import auth_email_bp
from App.routes.auth_email_reset import auth_email_reset_bp
from App.routes.auth_google import auth_google_bp

from App.routes.user_conversation_routes import user_conversation_bp
from App.routes.message_routes import message_bp
from App.routes.gemini_routes import gemini_api_bp
from App.routes.user_message_limit_routes import user_message_limit_bp
from App.routes.prompt_routes import user_prompt_bp

from App.routes.admin_user_routes import admin_user_bp
from App.routes.admin_category_routes import admin_category_bp
from App.routes.admin_language_routes import admin_language_bp
from App.routes.admin_prompt_routes import admin_prompt_bp
from App.routes.admin_system_settings_routes import admin_system_settings_bp

# from werkzeug.security import generate_password_hash, check_password_hash
# print("Hash:", generate_password_hash("admin"))


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = os.urandom(24).hex()

app.config.from_object(Config)

# Initialize database
# init_db(app)

# Initialize extensions
db.init_app(app)
mail = Mail(app)
app.mail = mail

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Debug: Print app config after initialization
# print(f"App Config - MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
# print(f"App Config - MAIL_PASSWORD: {app.config['MAIL_PASSWORD']}")

# Initialize OAuth
google = init_oauth(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(auth_email_bp)
app.register_blueprint(auth_email_reset_bp)
app.register_blueprint(auth_google_bp)

app.register_blueprint(gemini_api_bp, url_prefix="")
app.register_blueprint(user_conversation_bp)
app.register_blueprint(message_bp)
app.register_blueprint(user_message_limit_bp)
app.register_blueprint(user_prompt_bp)

app.register_blueprint(admin_user_bp, url_prefix="/admin")
app.register_blueprint(admin_category_bp, url_prefix="/admin")
app.register_blueprint(admin_language_bp, url_prefix="/admin")
app.register_blueprint(admin_prompt_bp, url_prefix="/admin")
app.register_blueprint(admin_system_settings_bp, url_prefix="/admin")

# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/home')
def home():
    # user_id = session.get('user_id')
    return render_template("index.html")

@app.route('/admin')
@login_required
@role_required(1)
def admin():
    return render_template("admin/index.html")


# Provide google to auth blueprint (optional, if needed)
auth_google_bp.google = google  # Attach google to the blueprint for use in routes

# Create database tables
with app.app_context():
    db.create_all()
    # create system settings
    if not SystemSettings.query.first():
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)