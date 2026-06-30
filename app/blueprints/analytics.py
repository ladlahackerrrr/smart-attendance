"""Analytics page blueprint."""

from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required

from app.models.student import Student
from app.models.attendance import Attendance
from app.models.academic import Semester


analytics_bp = Blueprint(
    'analytics',
    __name__,
    url_prefix='/analytics'
)


@analytics_bp.route('/')
@login_required
def dashboard():
    """Analytics dashboard."""

    # -------------------------
    # Total Students
    # -------------------------
    total_students = Student.query.filter_by(
        is_active=True
    ).count()

    # -------------------------
    # Today's Attendance
    # -------------------------
    today = date.today()

    present_today = Attendance.query.filter_by(
        date=today,
        status='present'
    ).count()

    absent_today = Attendance.query.filter_by(
        date=today,
        status='absent'
    ).count()

    # -------------------------
    # Overall Attendance %
    # -------------------------
    total_records = Attendance.query.count()

    present_records = Attendance.query.filter_by(
        status='present'
    ).count()

    average_attendance = (
        round(
            (present_records / total_records) * 100,
            2
        )
        if total_records > 0 else 0
    )

    # -------------------------
    # Semester-wise Attendance
    # -------------------------
    semester_stats = []

    semesters = Semester.query.all()

    for sem in semesters:

        records = (
            Attendance.query
            .join(Student)
            .join(Student.section)
            .filter_by(semester_id=sem.id)
            .all()
        )

        total = len(records)

        present = len([
            r for r in records
            if r.status == 'present'
        ])

        percentage = (
            round((present / total) * 100, 2)
            if total > 0 else 0
        )

        semester_stats.append({
            'semester': f'Sem {sem.number}',
            'attendance': percentage
        })

    # -------------------------
    # Student Lists
    # (<75%) + (>=75%)
    # -------------------------
    students = Student.query.filter_by(
        is_active=True
    ).all()

    defaulters = []
    good_students = []

    for student in students:

        print(student.name, student.get_attendance_percentage())

        percentage = (
            student.get_attendance_percentage()
        )

        student_data = {
            'name': student.name,
            'roll': student.roll_number,
            'semester':
                student.section.semester.number,
            'attendance':
                percentage
        }

        if percentage < 75:
            defaulters.append(
                student_data
            )
        else:
            good_students.append(
                student_data
            )

    # -------------------------
    # Render Page
    # -------------------------
    return render_template(
        'analytics/dashboard.html',

        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        average_attendance=average_attendance,

        semester_stats=semester_stats,

        defaulters=defaulters,
        good_students=good_students
    )