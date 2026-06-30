"""Student profile and list blueprint."""

from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required
from app.utils.decorators import teacher_or_admin_required
from app.models.student import Student
from app.models.academic import Department, Section
from app.extensions import db
from app.models.user import User
from sqlalchemy.orm import joinedload

students_bp = Blueprint('students', __name__, url_prefix='/students')

@students_bp.route('/')
@login_required
@teacher_or_admin_required
def list():
    """List students with search/filter options."""
    departments = Department.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()
    
    # Simple query
    students_query = Student.query.options(joinedload(Student.section).joinedload(Section.semester)).filter_by(is_active=True)

    # Filters
    semester_filter = request.args.get('semester',type=int)

    section_filter = request.args.get('section')

    # Join only ONCE
    if semester_filter or section_filter:students_query = students_query.join(Section)

    if semester_filter:students_query = students_query.filter( Section.semester_id == semester_filter)

    if section_filter:students_query = students_query.filter(Section.name == section_filter)

    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = students_query.order_by(Student.roll_number).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('students/list.html', 
                           pagination=pagination, 
                           students=pagination.items,
                           departments=departments,
                           sections=sections,
                           selected_semester=semester_filter,
                           selected_section=section_filter)

@students_bp.route('/<int:student_id>')
@login_required
@teacher_or_admin_required
def profile(student_id):
    """View detailed student attendance profile."""
    student = Student.query.get_or_404(student_id)
    return render_template('students/profile.html', student=student)
@students_bp.route('/add', methods=['POST'])
@login_required
@teacher_or_admin_required
def add_student():
    try:
        email = request.form.get('email').strip().lower()

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Student email already exists!', 'danger')
            return redirect(url_for('students.list'))

        user = User(
            full_name=request.form.get('name'),
            email=email,
            phone=request.form.get('phone'),
            role='student',
            is_active=True
        )

        user.set_password(request.form.get('password'))

        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            name=request.form.get('name'),
            roll_number=request.form.get('roll_number'),
            registration_number=request.form.get('registration_number'),
            email=email,
            phone=request.form.get('phone'),
            department_id=request.form.get('department_id'),
            section_id=request.form.get('section_id'),
            is_active=True
        )

        db.session.add(student)
        db.session.commit()

        flash('Student added successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding student: {str(e)}', 'danger')

    return redirect(url_for('students.list'))


@students_bp.route('/delete/<int:student_id>', methods=['POST'])
@login_required
@teacher_or_admin_required
def delete_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)

        student.is_active = False

        if student.user:
            student.user.is_active = False

        db.session.commit()

        flash('Student deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'danger')

    return redirect(url_for('students.list'))

@students_bp.route('/delete-all', methods=['POST'])
@login_required
@teacher_or_admin_required
def delete_all_students():
    try:
        students = Student.query.filter_by(
            is_active=True
        ).all()

        for student in students:
            student.is_active = False

            if student.user:
                student.user.is_active = False

        db.session.commit()

        flash(
            'All students deleted successfully!',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Error deleting students: {str(e)}',
            'danger'
        )

    return redirect(url_for('students.list'))