from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from App.database import db
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

    # New column 
    custom_css = db.Column(db.Text, nullable=True)
    model_api_key = db.Column(db.String(255), default="AIzaSyCJso-5IjKfj_mziMH12TYhdEBX9RzZaxs", nullable=False)

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


class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)  # Page title
    # content = db.Column(db.LONGTEXT, nullable=False)  # Use LONGTEXT for MySQL
    content = db.Column(db.Text(length=2**31-1), nullable=False)  # For PostgreSQL or SQLite
    slug = db.Column(db.String(191), unique=True, nullable=False)  # URL-friendly identifier
    
    # Status fields
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    is_homepage = db.Column(db.Boolean, default=False, nullable=False)  # Flag for homepage
    
    # Metadata
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # Assuming a users table
    updated_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                         onupdate=db.func.current_timestamp())
    
    # SEO fields (optional)
    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return (f'<Page: id={self.id}, title={self.title}, '
                f'slug={self.slug}, published={self.is_published}>')

    def save(self):
        """Helper method to save the page"""
        db.session.add(self)
        db.session.commit()

    def publish(self):
        """Helper method to publish the page"""
        self.is_published = True
        db.session.commit()

    def set_as_homepage(self):
        """Set this page as homepage and unset others"""
        # Unset existing homepage
        db.session.query(Page).filter(Page.is_homepage == True).update({"is_homepage": False})
        # Set this page as homepage
        self.is_homepage = True
        db.session.commit()

# Example usage:
"""
# Create a new page
new_page = Page(
    title="About Us",
    content="<h1>About Our Company</h1><p>Long HTML content here...</p>",
    slug="about-us",
    created_by="some-user-id",
    meta_title="About Our Company",
    meta_description="Learn more about our company's history and values"
)
new_page.save()

# Publish a page
new_page.publish()

# Set as homepage
new_page.set_as_homepage()
"""