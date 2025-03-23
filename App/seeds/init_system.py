# App/seeds/init_system.py
from ..models.system_settings import SystemSettings, Page
from ..models.models import User
from ..database import db

def init_system_settings():
    """Initialize system settings if they don't exist."""
    if not SystemSettings.query.first():
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()

    # Admin User
    if not User.query.filter(User.role == 1).first():
        admin = User(
            first_name='Damrong',
            last_name='Hol',
            username='damrong',
            role=1, # Explicitly set to Admin role
            email='hol.damrong@gmail.com'
        )
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

    # Seed SystemSettings (if not already present)
    if not db.session.query(SystemSettings).first():
        default_settings = SystemSettings(max_messages=5)
        db.session.add(default_settings)
        db.session.commit()
        print("✅ SystemSettings seeded successfully!")
    else:
        print("ℹ️ SystemSettings already exists, skipping seed.")

    # Create Home Page
    homepage = Page.query.filter_by(is_homepage=True, is_published=True).first()
    if not homepage:
        homepage = Page(
            title="Welcome",
            content="""
                <div class="d-flex flex-column justify-content-center align-items-center" style="height: calc(100vh - 60px)"/>
                    <h1>Welcome to Our Site</h1>
                    <p>This is the default homepage.</p>
                </div>
            """,
            slug="home",
            is_homepage=True,
            is_published=True,
            # created_by="system"
        )
        homepage.save()