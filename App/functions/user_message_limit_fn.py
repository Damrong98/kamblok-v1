from App.models.models import UserMessageLimit
from database import db
from datetime import date

# Assuming this is in your main app file
def check_and_update_message_limit(user_id):
    today = date.today()
    
    # Get or create the limit record for today
    limit = UserMessageLimit.query.filter_by(
        user_id=user_id,
        date=today
    ).first()
    
    if not limit:
        # Create a new limit record if it doesn't exist
        limit = UserMessageLimit(user_id=user_id, date=today, message_count=0)
        db.session.add(limit)
        db.session.flush()  # Ensure the record is in the session before proceeding
    
    if limit.can_send_message():
        limit.increment_count()
        db.session.commit()
        return True
    else:
        db.session.commit()  # Optional: only if you want to persist any other changes
        return False
