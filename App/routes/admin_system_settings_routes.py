# admin_stystem-settings_routes.py
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
# from models.userModel import User
from App.models.models import User, Prompt, Category, Language
from App.models.system_settings import SystemSettings
from App.database import db
from utils import role_required # Import from utils

admin_system_settings_bp = Blueprint('admin_system_settings_routes', __name__)


# Routes
@admin_system_settings_bp.route('/system_settings')
@role_required(1,2)
def system_settings():
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings(model_api_key="default_api_key")
        db.session.add(settings)
        db.session.commit()
    return render_template('/admin/system_settings/system_settings.html', settings=settings)

@admin_system_settings_bp.route('/api/update_setting', methods=['POST'])
@role_required(1)
def update_setting():
    data = request.get_json()
    settings = SystemSettings.query.get(data['id'])
    
    try:
        if data['field'] == 'max_messages':
            settings.max_messages = int(data['value'])
        elif data['field'] == 'logo_html':
            settings.logo_html = data['value']
        elif data['field'] == 'custom_css':
            settings.custom_css = data['value']
        elif data['field'] == 'model_api_key':
            settings.model_api_key = data['value']
        
        db.session.commit()
        return jsonify({'success': True, 'value': data['value']})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    





# get app logo
# @admin_system_settings_bp.route("/api/system_settings/get_logo_html", methods=["GET"])
# def get_logo_settings():
#     settings = SystemSettings.query.first()
#     if settings and settings.logo_html:
#         return jsonify({"logo_html": settings.logo_html})
#     return jsonify({"logo_html": """<h4 class="mb-0">kamblok</h4>"""})  # Return empty if not set


@admin_system_settings_bp.route("/api/system_settings/get_logoAndCSS", methods=["GET"])
def get_logoAndCSS_settings():
    settings = SystemSettings.query.first()
    if settings:
        return jsonify({
            "logo_html": settings.logo_html if settings.logo_html else "<h4 class='mb-0'>kamblok</h4>",
            "custom_css": settings.custom_css if settings.custom_css else ""
        })
    return jsonify({
        "logo_html": "<h4 class='mb-0'>kamblok</h4>",
        "custom_css": ""
    })