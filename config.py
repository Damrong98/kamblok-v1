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

    # Database configuration variables
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'my_database')

    # Construct the MySQL URI for local fallback
    MYSQL_URI = (
        f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}'
        f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )

    # Use DATABASE_URL from Railway if available, otherwise fallback to MySQL URI
    SQLALCHEMY_DATABASE_URI = os.getenv('MYSQL_URL') or MYSQL_URI
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