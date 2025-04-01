from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from App.database import db
import uuid
import random

from App.models.system_settings import SystemSettings

# Initialize SQLAlchemy (this will be imported and configured in your Flask app)
# db = SQLAlchemy()


# Define the User table
class User(db.Model):
    __tablename__ = 'users'

    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(50), nullable=False)  # New: First name
    last_name = db.Column(db.String(50), nullable=False)   # New: Last name
    username = db.Column(db.String(50), unique=True, nullable=True)  # Already unique
    date_of_birth = db.Column(db.Date, nullable=True)     # New: Date of birth
    phone_number = db.Column(db.String(20), unique=True, nullable=True)  # New: Phone number (unique)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255))
    role = db.Column(db.Integer, default=0, nullable=False)  # Default role is 3 (User)
    max_messages = db.Column(db.Integer, default=0, nullable=False)
    registration_type = db.Column(db.String(10), nullable=True)  # 'email', 'google', or 'phone'
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    conversations = db.relationship("Conversation", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_role_name(self):
        role_map = {
            0: 'User',
            1: 'Admin',
            2: 'Editor',
        }
        return role_map.get(self.role, 'Unknown')
    
    def generate_username(self):
        """
        Generate a unique username based on first_name and last_name.
        Format: first_name.last_name.random_number (e.g., john.doe.123)
        Keeps generating until a unique username is found.
        """
        base_username = f"{self.first_name.lower()}.{self.last_name.lower()}"
        username = base_username
        suffix = random.randint(1, 9999)  # Random number to ensure uniqueness

        # Keep trying until a unique username is found
        while User.query.filter_by(username=username).first():
            username = f"{base_username}.{suffix}"
            suffix = random.randint(1, 9999)

        return username

    def __repr__(self):
        return f'<User {self.username}>'

# Define the Conversation table
class Conversation(db.Model):
    __tablename__ = 'conversations'

    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    user = db.relationship("User", back_populates="conversations")
    messages = db.relationship("Message", back_populates="conversation")

    def __repr__(self):
        return f'<Conversation {self.title} for User {self.user_id}>'

# Define the Message table
class Message(db.Model):
    __tablename__ = 'messages'

    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    sender = db.Column(db.Enum('user', 'model', name='sender_type'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    message_html = db.Column(db.Text, nullable=False)
    api_response_time = db.Column(db.Float)  # Optional: time in seconds for AI response
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    conversation = db.relationship("Conversation", back_populates="messages")
    api_logs = db.relationship("APILog", back_populates="message")

    def __repr__(self):
        return f'<Message {self.sender}: {self.message_text[:20]}...>'

# Define the API Log table (optional)
class APILog(db.Model):
    __tablename__ = 'api_logs'

    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = db.Column(db.String(36), db.ForeignKey('messages.id', ondelete='SET NULL'))
    api_endpoint = db.Column(db.String(255))
    request_payload = db.Column(db.Text)
    response_text = db.Column(db.Text)
    status_code = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    message = db.relationship("Message", back_populates="api_logs")

    def __repr__(self):
        return f'<APILog for Message {self.message_id}>'
    

# Add this new UserMessageLimit table after your other model definitions
class UserMessageLimit(db.Model):
    __tablename__ = 'user_message_limits'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message_count = db.Column(db.Integer, default=0, nullable=False)
    reset_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(hours=6), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())

    # Relationships
    user = db.relationship("User", backref="message_limits")

    # Ensure unique constraint for one record per user per day
    # __table_args__ = (
    #     db.UniqueConstraint('user_id', 'date', name='uq_user_date'),
    # )

    # Unique constraint for one record per user
    __table_args__ = (
        db.UniqueConstraint('user_id', name='uq_user'),
    )

    def __repr__(self):
        return f'<UserMessageLimit for User {self.user_id} until {self.reset_time}: {self.message_count}/10>'

    def can_send_message(self):
        system_settings = db.session.query(SystemSettings).first()
        system_max_messages = system_settings.max_messages if system_settings else 0
        return self.message_count < (self.user.max_messages + system_max_messages)

    def increment_count(self):
        if self.can_send_message():
            self.message_count += 1
            return True
        return False

    def get_remaining_seconds(self):
        now = datetime.now(timezone.utc)
        reset_time = self.reset_time
        if reset_time.tzinfo is None:
            reset_time = reset_time.replace(tzinfo=timezone.utc)
        if now >= reset_time:
            return 0
        return (reset_time - now).total_seconds()
    
"""
Prompts
Table: prompts, categories, languages
"""

# Modified Prompt table with foreign keys to Category and Language
class Prompt(db.Model):
    __tablename__ = 'prompts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)  # The actual prompt entered by the user
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)  # Foreign key to Category
    language_id = db.Column(db.String(36), db.ForeignKey('languages.id'), nullable=True)  # Foreign key to Language
    is_active = db.Column(db.Boolean, default=True)  # Optional: to mark if the prompt is still in use
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    user = db.relationship("User", backref="prompts")
    category = db.relationship("Category", backref="prompts")
    language = db.relationship("Language", backref="prompts")

    def __repr__(self):
        return f'<Prompt by User {self.user_id}: {self.prompt_text[:20]}...>'
    

# Category table
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)  # Category name (e.g., "General", "Tech")
    description = db.Column(db.Text, nullable=True)  # Optional description of the category
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Category {self.name}>'

# Language table
class Language(db.Model):
    __tablename__ = 'languages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(10), nullable=False, unique=True)  # Language code (e.g., "en", "es")
    name = db.Column(db.String(50), nullable=False)  # Language name (e.g., "English", "Spanish")
    status = db.Column(db.String(20), nullable=False, default='active')  # Language status (e.g., "active", "inactive", "default")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def set_as_default(self):
            """Sets this language as the default language"""
            # First, set all other languages to 'active' status
            db.session.query(Language).filter(Language.id != self.id).update({'status': 'active'})
            # Then set this language as 'default'
            self.status = 'default'
            db.session.commit()

    def __repr__(self):
        return f'<Language {self.name} ({self.code})>'

# Example Flask app setup (to be included in your main app file)
"""
from flask import Flask
from database import db  # Import the db object from this file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db'  # Or your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with the app
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
"""