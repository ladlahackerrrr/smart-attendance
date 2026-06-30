"""Teacher blueprint."""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.decorators import teacher_required
from app.services.analytics_service import get_dashboard_stats
from app.services.attendance_service import get_teacher_classes

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    """Teacher dashboard home page."""
    stats = get_dashboard_stats(current_user)
    classes = get_teacher_classes(current_user.id)
    return render_template('teacher/dashboard.html', stats=stats, classes=classes)
@teacher_bp.route('/classes')
@login_required
@teacher_required
def classes():

    assignments = current_user.teaching_assignments

    return render_template(
        'teacher/classes.html',
        assignments=assignments
    )