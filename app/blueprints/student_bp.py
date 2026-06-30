"""Student dashboard blueprint."""

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.utils.decorators import student_required
from app.models.student import Student
from app.services.analytics_service import get_student_dashboard_stats

student_bp = Blueprint('student_bp', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard home page."""
    # Find student profile linked to user
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        abort(404, description="Student profile not found.")
        
    stats = get_student_dashboard_stats(student.id)
    return render_template('student/dashboard.html', student=student, stats=stats)

@student_bp.route('/attendance')
@login_required
@student_required
def attendance():
    """Detailed student attendance page."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        abort(404, description="Student profile not found.")
    return render_template('student/attendance.html', student=student)

@student_bp.route('/analytics')
@login_required
@student_required
def analytics():
    """Student personal analytics charts."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        abort(404, description="Student profile not found.")
    return render_template('student/analytics.html', student=student)
