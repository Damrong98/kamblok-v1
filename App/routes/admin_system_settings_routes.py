# admin_stystem-settings_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
# from models.userModel import User
from App.models.models import User, Prompt, Category, Language
from App.models.system_settings import SystemSettings
from database import db
from utils import login_required  # Import from utils

admin_system_settings_bp = Blueprint('admin_system_settings_routes', __name__)


# Routes
@admin_system_settings_bp.route('/system_settings')
def system_settings():
    return render_template('/admin/system_settings/system_settings.html')

# Read settings
@admin_system_settings_bp.route('/api/system_settings', methods=['GET'])
def get_system_settings():
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()
    
    return jsonify({
        'id': settings.id,
        'max_messages': settings.max_messages,
        'logo_html': settings.logo_html,
        'email_registered_count': settings.email_registered_count,
        'google_registered_count': settings.google_registered_count,
        'phone_registered_count': settings.phone_registered_count,
        'total_registered_count': settings.total_registered_count,
        'created_at': settings.created_at.isoformat(),
        'updated_at': settings.updated_at.isoformat()
    })

# Update settings (only max_messages)
@admin_system_settings_bp.route('/api/system_settings', methods=['PUT'])
def update_system_settings():
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
    
    data = request.get_json()
    try:
        settings.max_messages = int(data['max_messages'])
        settings.logo_html = data['logo_html']
        db.session.commit()
        return jsonify({'message': 'Settings updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

# get app logo
@admin_system_settings_bp.route("/api/system_settings/get_logo_html", methods=["GET"])
def get_logo_settings():
    settings = SystemSettings.query.first()
    if settings and settings.logo_html:
        return jsonify({"logo_html": settings.logo_html})
    return jsonify({"logo_html": """<h4 class="mb-0">kamblok</h4>"""})  # Return empty if not set