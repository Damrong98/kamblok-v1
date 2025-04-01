from flask import Blueprint, jsonify, session
from App.functions.user_message_limit_fn import check_and_update_message_limit  # Import the function
from utils import login_required  # Import from utils
from App.models.models import UserMessageLimit
from datetime import datetime, timedelta, timezone



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
    

# API Route - With user limit logic
@user_message_limit_bp.route('/api/message_limit', methods=['GET'])
def index_api():
    try:
        # Get user_id from session
        auth_id = session.get('user_id')
        if not auth_id:
            return jsonify({'error': 'User not authenticated'}), 401

        # Query the user's message limit
        limit = UserMessageLimit.query.filter_by(user_id=auth_id).first()
        
        # Calculate remaining seconds and message count
        remaining_seconds = limit.get_remaining_seconds() if limit else 0
        message_count = limit.message_count if limit else 0
        
        # Prepare response
        if limit:
            # Ensure reset_time is timezone-aware
            reset_time = limit.reset_time
            if reset_time.tzinfo is None:
                reset_time = reset_time.replace(tzinfo=timezone.utc)
                limit.reset_time = reset_time  # Update object for consistency
            
            response = {
                'user_id': auth_id,
                'message_count': message_count,
                'remaining_seconds': remaining_seconds,
                'reset_time': reset_time.isoformat(),
                'can_send_message': limit.can_send_message()
            }
        else:
            response = {
                'user_id': auth_id,
                'message_count': message_count,
                'remaining_seconds': remaining_seconds,
                'reset_time': (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(),
                'can_send_message': True
            }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error in index_api: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500