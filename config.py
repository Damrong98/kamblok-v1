# config.py
import os
from dotenv import load_dotenv

load_dotenv()

app_key = os.urandom(24).hex()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', app_key)

    # Database configuration
    # SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///users.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database configuration for MySQL on localhost
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')  # Default MySQL user in WAMP
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')      # Default is empty in WAMP
    DB_HOST = os.getenv('DB_HOST', 'localhost')     # Localhost
    DB_PORT = os.getenv('DB_PORT', '3306')          # Default MySQL port
    DB_NAME = os.getenv('DB_NAME', 'my_database')   # Your database name

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # # Database configuration variables for Google Cloud SQL (MySQL)
    # DB_USERNAME = os.getenv('DB_USERNAME', '<username>')
    # DB_PASSWORD = os.getenv('DB_PASSWORD', '<password>')
    # DB_NAME = os.getenv('DB_NAME', '<database_name>')
    # DB_PROJECT_ID = os.getenv('DB_PROJECT_ID', '<project_id>')
    # DB_REGION = os.getenv('DB_REGION', '<region>')
    # DB_INSTANCE_NAME = os.getenv('DB_INSTANCE_NAME', '<instance_name>')

    # SQLALCHEMY_DATABASE_URI = (
    #     f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@/{DB_NAME}'
    #     f'?unix_socket=/cloudsql/{DB_PROJECT_ID}:{DB_REGION}:{DB_INSTANCE_NAME}'
    # )
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    
    # Debug prints
    # print(f"Config - MAIL_SERVER: {MAIL_SERVER}")
    # print(f"Config - MAIL_PORT: {MAIL_PORT}")
    # print(f"Config - MAIL_USE_TLS: {MAIL_USE_TLS}")
    # print(f"Config - MAIL_USERNAME: {MAIL_USERNAME}")
    # print(f"Config - MAIL_PASSWORD: {MAIL_PASSWORD}")