"""Role-based access control decorators."""

from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to restrict access to teacher or admin users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['teacher', 'admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def teacher_or_admin_required(f):
    """Decorator to restrict access to teachers or admin (alias)."""
    return teacher_required(f)

def student_required(f):
    """Decorator to restrict access to student users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
