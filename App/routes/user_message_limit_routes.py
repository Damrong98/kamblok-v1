from flask import Blueprint, jsonify, session
from App.functions.user_message_limit_fn import check_and_update_message_limit  # Import the function
from utils import login_required  # Import from utils



# Create a Blueprint instance
user_message_limit_bp = Blueprint('user_message_limit_routes', __name__, static_folder="static", template_folder="templates")


# routes api  
@user_message_limit_bp.route('/api/user_message_limit/check_limit', methods=['POST'])
@login_required
def check_message_limit_for_today_api():
    auth_id = session.get('user_id')

    # check message limit
    can_send = check_and_update_message_limit(auth_id)

    if can_send:
        # print("Message sent successfully")
        return jsonify({
            "status": "success",
            "message": "Message sent successfully"
        })
    else:
        # print("Message limit reached")
        return jsonify({
            "status": "error",
            "message": "Message limit reached"
        })