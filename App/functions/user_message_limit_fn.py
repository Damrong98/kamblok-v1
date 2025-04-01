from App.models.models import UserMessageLimit
from App.database import db
from datetime import datetime, timedelta, timezone

# Assuming this is in your main app file
# def check_and_update_message_limit(user_id):
#     today = date.today()
    
#     # Get or create the limit record for today
#     limit = UserMessageLimit.query.filter_by(
#         user_id=user_id,
#         date=today
#     ).first()
    
#     if not limit:
#         # Create a new limit record if it doesn't exist
#         limit = UserMessageLimit(user_id=user_id, date=today, message_count=0)
#         db.session.add(limit)
#         db.session.flush()  # Ensure the record is in the session before proceeding
    
#     if limit.can_send_message():
#         limit.increment_count()
#         db.session.commit()
#         return True
#     else:
#         db.session.commit()  # Optional: only if you want to persist any other changes
#         return False
    
def check_and_update_message_limit(user_id):
    now = datetime.now(timezone.utc)  # Timezone-aware
    
    # Get the limit record for the user (there should only be one)
    limit = UserMessageLimit.query.filter_by(user_id=user_id).first()
    
    # If no limit exists or the reset time has passed, reset or create the limit
    if not limit:
        # Create new limit with 6-hour reset period if none exists
        limit = UserMessageLimit(
            user_id=user_id,
            message_count=0,
            reset_time=now + timedelta(hours=6)
        )
        db.session.add(limit)
        db.session.flush()
    else:
        # Ensure reset_time is timezone-aware (assume UTC if naive)
        reset_time = limit.reset_time
        if reset_time.tzinfo is None:
            reset_time = reset_time.replace(tzinfo=timezone.utc)
            limit.reset_time = reset_time  # Update the object to maintain consistency
        
        # Check if reset time has passed
        if now >= reset_time:
            # Reset existing limit instead of creating new record
            limit.message_count = 0
            limit.reset_time = now + timedelta(hours=6)
            db.session.flush()
    
    if limit.can_send_message():
        limit.increment_count()
        db.session.commit()
        return True
    else:
        db.session.commit()
        return False
