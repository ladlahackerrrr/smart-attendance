"""Authentication and User management services."""

from datetime import datetime
from app.extensions import db
from app.models.user import User

def authenticate_user(email, password):
    """Authenticate user by email and password, updating last_login."""
    user = User.query.filter_by(email=email.lower().strip()).first()
    if user and user.check_password(password):
        if not user.is_active:
            return None
        user.last_login = datetime.utcnow()
        db.session.commit()
        return user
    return None

def create_user(email, password, full_name, role, phone=None):
    """Create a new user."""
    user = User(
        email=email.lower().strip(),
        full_name=full_name,
        role=role,
        phone=phone
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def change_password(user_id, old_password, new_password):
    """Verify old password and change it to the new password."""
    user = User.query.get(user_id)
    if user and user.check_password(old_password):
        user.set_password(new_password)
        db.session.commit()
        return True, "Password updated successfully."
    return False, "Incorrect old password."

def update_profile(user_id, full_name, phone=None, theme_preference=None):
    """Update user profile fields."""
    user = User.query.get(user_id)
    if user:
        user.full_name = full_name
        if phone is not None:
            user.phone = phone
        if theme_preference is not None:
            user.theme_preference = theme_preference
        db.session.commit()
        return True, user
    return False, "User not found."

def get_user_by_id(user_id):
    """Retrieve a user by ID."""
    return User.query.get(user_id)

def get_all_teachers():
    """Retrieve all teachers who are active."""
    return User.query.filter_by(role='teacher', is_active=True).all()

def get_all_users(role=None, page=1, per_page=20):
    """Retrieve paginated list of users, optionally filtered by role."""
    query = User.query
    if role:
        query = query.filter_by(role=role)
    return query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
