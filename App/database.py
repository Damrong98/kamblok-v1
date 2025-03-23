# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# def cleanup_old_limits(app):
#     with app.app_context():
#         old_date = date.today() - timedelta(days=30)
#         UserMessageLimit.query.filter(UserMessageLimit.date < old_date).delete()
#         db.session.commit()
#         print(f"Cleaned up records older than {old_date}")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()