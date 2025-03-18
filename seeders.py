from flask import Flask
from database import db
from App.models.models import User, Conversation, Message, Prompt  # Import from your models.py
from App.models.system_settings import SystemSettings
from app import app
import uuid

# Recreate the database tables and add data
with app.app_context():
    db.drop_all()  # Optional: ensures all old tables are dropped
    db.create_all()  # Creates tables based on current models


    # Seed SystemSettings (if not already present)
    if not db.session.query(SystemSettings).first():
        default_settings = SystemSettings(max_messages=5)
        db.session.add(default_settings)
        db.session.commit()
        print("✅ SystemSettings seeded successfully!")
    else:
        print("ℹ️ SystemSettings already exists, skipping seed.")

    # Add User 1
    admin = User(
        first_name='Admin',
        last_name='KB',
        username='admin',
        role=1, # Explicitly set to Admin role
        email='admin@example.com'
    )
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()
    
    # Add User 1
    user1 = User(
        first_name='User1',
        last_name='KB',
        username='user1', 
        email='user1@example.com'
    )
    user1.set_password('user1')
    db.session.add(user1)
    db.session.commit()

    # Add User 2
    user2 = User(
        first_name='User2',
        last_name='KB',
        username='user2', 
        email='user2@example.com'
    )
    user2.set_password('user2')
    db.session.add(user2)
    db.session.commit()

    # Add Conversation for User 1 (Alice)
    convo1 = Conversation(user_id=user1.id, title="Alice's Weather Chat")
    db.session.add(convo1)
    db.session.commit()

    # Add Messages for Alice's Conversation
    msg1_alice = Message(
        conversation_id=convo1.id,
        sender="user",
        message_text="What’s the weather like today?",
        message_html="What’s the weather like today?"
    )
    msg2_alice = Message(
        conversation_id=convo1.id,
        sender="model",
        message_text="It’s sunny with a high of 72°F!",
        message_html="It’s sunny with a high of 72°F!",
        api_response_time=0.8
    )
    db.session.add_all([msg1_alice, msg2_alice])
    db.session.commit()

    # Add Conversation for User 2 (Bob)
    convo2 = Conversation(user_id=user2.id, title="Bob's Food Chat")
    db.session.add(convo2)
    db.session.commit()

    # Add Messages for Bob's Conversation
    msg1_bob = Message(
        conversation_id=convo2.id,
        sender="user",
        message_text="What’s a good recipe for dinner?",
        message_html="",
    )
    msg2_bob = Message(
        conversation_id=convo2.id,
        sender="model",
        message_text="Try a chicken stir-fry with veggies and soy sauce!",
        message_html="Try a chicken stir-fry with veggies and soy sauce!",
        api_response_time=1.2
    )
    msg3_bob = Message(
        conversation_id=convo2.id,
        sender="user",
        message_text="Sounds good, thanks!",
        message_html="",
    )
    db.session.add_all([msg1_bob, msg2_bob, msg3_bob])
    db.session.commit()

    # Add 5 Prompts by Admin with Khmer/English and Teaching/Normal
    admin_prompts = [
        Prompt(
            user_id=admin.id,
            prompt_text="Teach how to greet someone in Khmer",
        ),
        Prompt(
            user_id=admin.id,
            prompt_text="Write a simple English greeting",
        ),
        Prompt(
            user_id=admin.id,
            prompt_text="Explain Khmer numbers 1-10",
        ),
        Prompt(
            user_id=admin.id,
            prompt_text="Create a short English story",
        ),
        Prompt(
            user_id=admin.id,
            prompt_text="Teach basic Khmer phrases for travelers",
        )
    ]
    db.session.add_all(admin_prompts)
    db.session.commit()

    print("Database recreated and populated with 2 users, their conversations, and messages")

# Optional: Query and display the data to verify
with app.app_context():
    # Check users
    users = User.query.all()
    for user in users:
        print(f"User: {user.username}, Email: {user.email}")

    # Check conversations and messages
    conversations = Conversation.query.all()
    for convo in conversations:
        print(f"\nConversation: {convo.title} (User ID: {convo.user_id}) (Convo ID: {convo.id})")
        for msg in convo.messages:
            print(f"  {msg.sender}: {msg.message_text}")

# Check prompts
    prompts = Prompt.query.all()
    for prompt in prompts:
        print(f"\nPrompt by {prompt.user.username}: {prompt.prompt_text}")
        # print(f"  Type: {prompt.type}, Language: {prompt.language}, Active: {prompt.is_active}")