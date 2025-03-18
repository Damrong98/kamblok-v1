from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db
import uuid
import random

# Initialize SQLAlchemy (this will be imported and configured in your Flask app)
# db = SQLAlchemy()

# System Settings
class SystemSettings(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    max_messages = db.Column(db.Integer, default=5, nullable=False)  # Default system-wide max messages

    # New column to store HTML for the logo
    logo_html = db.Column(db.Text, nullable=True)

    # Registration tracking
    email_registered_count = db.Column(db.Integer, default=0, nullable=False)
    google_registered_count = db.Column(db.Integer, default=0, nullable=False)
    phone_registered_count = db.Column(db.Integer, default=0, nullable=False)
    total_registered_count = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return (f'<SystemSettings: max_messages={self.max_messages}, '
                f'Email={self.email_registered_count}, Google={self.google_registered_count}, '
                f'Phone={self.phone_registered_count}, Total={self.total_registered_count}>')

    @classmethod
    def update_registration_count(cls, registration_type):
        system_settings = db.session.query(cls).first()
        if not system_settings:
            system_settings = cls()
            db.session.add(system_settings)

        if registration_type == "email":
            system_settings.email_registered_count += 1
        elif registration_type == "google":
            system_settings.google_registered_count += 1
        elif registration_type == "phone":
            system_settings.phone_registered_count += 1

        system_settings.total_registered_count += 1  # Always update total count
        db.session.commit()

    # Usage
    # SystemSettings.update_registration_count("email")  # For email registration
    # SystemSettings.update_registration_count("google")  # For Google registration
    # SystemSettings.update_registration_count("phone")  # For phone registration