"""Authentication blueprint."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.services.auth_service import authenticate_user
from app.extensions import login_manager
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    """Callback to load user object from session ID."""
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = authenticate_user(email, password)
        if user:
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name}!", "success")
            
            # Handle redirection to next parameter if it exists
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect_to_dashboard(user)
        else:
            flash("Invalid email or password.", "error")

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

def redirect_to_dashboard(user):
    """Utility to redirect user to their dashboard based on role."""
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'teacher':
        return redirect(url_for('teacher.dashboard'))
    elif user.role == 'student':
        return redirect(url_for('student_bp.dashboard'))
    return redirect(url_for('landing'))
