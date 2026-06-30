"""Reports generator blueprint."""

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.utils.decorators import teacher_or_admin_required
from app.models.academic import Department, Section
from app.models.student import Student

reports_bp = Blueprint(
    'reports',
    __name__,
    url_prefix='/reports'
)


@reports_bp.route('/')
@login_required
@teacher_or_admin_required
def index():

    departments = Department.query.filter_by(
        is_active=True
    ).all()

    students = []

    department_id = request.args.get(
        'department'
    )

    section_name = request.args.get(
        'section'
    )

    report_type = request.args.get(
        'report_type'
    )

    query = Student.query.filter_by(
        is_active=True
    )

    if department_id:
        query = query.filter_by(
            department_id=department_id
        )

    if section_name:
        query = (
            query.join(Section)
            .filter(
                Section.name == section_name
            )
        )

    students = query.all()

    # Defaulters only
    if report_type == 'defaulters':

        students = [
            s for s in students
            if s.get_attendance_percentage() < 75
        ]

    return render_template(
        'reports/index.html',
        departments=departments,
        students=students
    )