# utils.py
from functools import wraps
from flask import session, flash, redirect, url_for

# check user login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # flash('Please login first', 'error')
            # return redirect(url_for('auth.login'))  # Note: assumes 'auth' Blueprint
            return redirect(url_for('home', _external=True, _scheme="https")) 
        return f(*args, **kwargs)
    return decorated_function


# check user role
def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the required roles
    Roles:
        0: 'User'
        1: 'Admin'
        2: 'Editor'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check if user is logged in
            if 'user_id' not in session:
                flash('Please login first', 'error')
                return redirect(url_for('auth.login', _external=True, _scheme="https"))
            
            # Role mapping
            role_map = {
                0: 'User',
                1: 'Admin',
                2: 'Editor',
            }
            
            # Get user's role from session (assuming it's stored there)
            user_role = session.get('user_role')  # You'll need to store this during login
            
            # Check if user's role is in allowed roles
            if user_role not in allowed_roles:
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('index'))  # Redirect to home or unauthorized page
            
            # Convert role number to role name for potential use in the function
            session['role_name'] = role_map.get(user_role, 'Unknown')
            return f(*args, **kwargs)
        return decorated_function
    return decorator



# example of usages
# @app.route('/admin-panel')
# @login_required
# @role_required(1)  # Only Admins allowed
# def admin_panel():
#     return "Welcome to Admin Panel"

# @app.route('/editor-dashboard')
# @login_required
# @role_required(1, 2)  # Admins and Editors allowed
# def editor_dashboard():
#     return "Welcome to Editor Dashboard"

# @app.route('/user-profile')
# @login_required
# @role_required(1, 2, 3)  # All roles allowed
# def user_profile():
#     return "Welcome to User Profile"