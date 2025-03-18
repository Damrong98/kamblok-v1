""""
Use in: 
"""
from flask import Flask
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

def init_oauth(app: Flask):
    load_dotenv()
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    return google