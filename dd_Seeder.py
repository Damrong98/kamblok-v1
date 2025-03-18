from app import app
from models.userModel import User
from database import db

# Recreate the database tables
with app.app_context():
    db.drop_all()  # Optional: ensures all old tables are dropped
    db.create_all()  # Creates tables based on current models

    # Add the test user
    user = User(username='admin', email='test@example.com')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()
    print("Database recreated and test user added")