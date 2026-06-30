"""Attendance tracking blueprint."""

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for
)
from flask_login import (
    login_required,
    current_user
)

from app.models.academic import Department

attendance_bp = Blueprint(
    'attendance',
    __name__,
    url_prefix='/attendance'
)


@attendance_bp.route('/mark')
@login_required
def mark():
    """Attendance marking interface."""

    # Allow only teacher or admin
    if current_user.role not in ['teacher', 'admin']:
        flash(
            'You are not authorized to access attendance.',
            'danger'
        )
        return redirect(url_for('index'))

    departments = Department.query.filter_by(
        is_active=True
    ).all()

    return render_template(
        'attendance/mark.html',
        departments=departments
    )


@attendance_bp.route('/history')
@login_required
def history():
    """Attendance history viewing page."""

    # Allow only teacher or admin
    if current_user.role not in ['teacher', 'admin']:
        flash(
            'You are not authorized to access attendance history.',
            'danger'
        )
        return redirect(url_for('index'))

    departments = Department.query.filter_by(
        is_active=True
    ).all()

    return render_template(
        'attendance/history.html',
        departments=departments
    )