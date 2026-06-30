"""Admin dashboard blueprint."""

import pandas as pd
from app.models.student import Student
from werkzeug.utils import secure_filename
import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from flask import flash
from app.utils.decorators import admin_required
from app.services.analytics_service import get_dashboard_stats
from app.models.academic import Department, Program, Semester, Section
from app.models.subject import Subject, SectionSubject
from app.models.user import User
from app.extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard landing page."""
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)

# Skeletons for CRUD routes (Phase 1)

# ==========================
# Department 
# ==========================
@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    departments_list = Department.query.filter_by(is_active=True).all()
    return render_template('admin/departments.html', departments=departments_list)

# ==========================
# Department CRUD
# ==========================

@admin_bp.route('/departments/add', methods=['POST'])
@login_required
@admin_required
def add_department():
    try:
        code = request.form.get('code').strip()
        name = request.form.get('name').strip()
        description = request.form.get('description')

        # Find department by code
        existing = Department.query.filter_by(code=code).first()

        if existing:

            # Restore inactive department
            if not existing.is_active:
                existing.name = name
                existing.description = description
                existing.is_active = True

                db.session.commit()

                flash(
                    'Inactive department restored successfully!',
                    'success'
                )

                return redirect(url_for('admin.departments'))

            # Already active
            flash('Department already exists!', 'danger')
            return redirect(url_for('admin.departments'))

        # Create new department
        department = Department(
            code=code,
            name=name,
            description=description,
            is_active=True
        )

        db.session.add(department)
        db.session.commit()

        flash('Department added successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding department: {str(e)}', 'danger')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/departments/delete/<int:department_id>', methods=['POST'])
@login_required
@admin_required
def delete_department(department_id):
    try:
        department = Department.query.get_or_404(department_id)

        db.session.delete(department)

        db.session.commit()

        flash('Department deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting department: {str(e)}', 'danger')

    return redirect(url_for('admin.departments'))
# ==========================
# Program
# ==========================

@admin_bp.route('/programs')
@login_required
@admin_required
def programs():
    programs_list = Program.query.filter_by(is_active=True).all()
    departments_list = Department.query.filter_by(is_active=True).all()
    return render_template('admin/programs.html', programs=programs_list, departments=departments_list)

# ==========================
# Program CRUD
# ==========================

@admin_bp.route('/programs/add', methods=['POST'])
@login_required
@admin_required
def add_program():
    try:
        code = request.form.get('code').strip()
        name = request.form.get('name').strip()
        department_id = request.form.get('department_id')
        duration_years = request.form.get('duration_years')

        existing = Program.query.filter_by(code=code).first()

        if existing:

            if not existing.is_active:
                existing.name = name
                existing.department_id = department_id
                existing.duration_years = duration_years
                existing.is_active = True

                db.session.commit()

                flash(
                    'Inactive program restored successfully!',
                    'success'
                )

                return redirect(url_for('admin.programs'))

            flash('Program already exists!', 'danger')
            return redirect(url_for('admin.programs'))

        program = Program(
            code=code,
            name=name,
            department_id=department_id,
            duration_years=duration_years,
            is_active=True
        )

        db.session.add(program)
        db.session.commit()

        flash('Program added successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding program: {str(e)}', 'danger')

    return redirect(url_for('admin.programs'))


@admin_bp.route('/programs/delete/<int:program_id>', methods=['POST'])
@login_required
@admin_required
def delete_program(program_id):
    try:
        program = Program.query.get_or_404(program_id)

        program.is_active = False

        db.session.commit()

        flash('Program deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting program: {str(e)}', 'danger')

    return redirect(url_for('admin.programs'))

# ==========================
# Semester
# ==========================
@admin_bp.route('/semesters')
@login_required
@admin_required
def semesters():
    semesters_list = Semester.query.filter_by(is_active=True).all()
    programs = Program.query.filter_by(is_active=True).all()
    return render_template('admin/semesters.html', semesters=semesters_list,programs=programs)
@admin_bp.route('/semesters/add', methods=['POST'])
@login_required
@admin_required
def add_semester():

    try:
        semester = Semester(
            number=request.form.get('number'),
            label=request.form.get('label'),
            program_id=request.form.get('program_id'),
            is_active=True
        )

        db.session.add(semester)
        db.session.commit()

        flash(
            'Semester added successfully!',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Error: {str(e)}',
            'danger'
        )

    return redirect(url_for('admin.semesters'))
@admin_bp.route('/semesters/delete/<int:semester_id>',
                methods=['POST'])
@login_required
@admin_required
def delete_semester(semester_id):

    try:
        semester = Semester.query.get_or_404(
            semester_id
        )

        # Check if semester has sections
        section_ids = [
            s.id for s in semester.sections
        ]

        students_exist = Student.query.filter(
            Student.section_id.in_(section_ids)
        ).first()

        if students_exist:
            flash(
                'Cannot delete semester. '
                'Students are assigned to it.',
                'danger'
            )

            return redirect(
                url_for('admin.semesters')
            )

        db.session.delete(semester)
        db.session.commit()

        flash(
            'Semester deleted successfully!',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Error: {str(e)}',
            'danger'
        )

    return redirect(url_for('admin.semesters'))
# ==========================
# Sections 
# ==========================

@admin_bp.route('/sections')
@login_required
@admin_required
def sections():
    sections_list = Section.query.filter_by(is_active=True).all()
    semesters = Semester.query.filter_by(is_active=True).all()
    return render_template('admin/sections.html', sections=sections_list,semesters=semesters)
@admin_bp.route('/sections/add', methods=['POST'])
@login_required
@admin_required
def add_section():

    try:
        section = Section(
            name=request.form.get('name'),
            semester_id=request.form.get(
                'semester_id'
            ),
            max_strength=request.form.get(
                'max_strength'
            ),
            is_active=True
        )

        db.session.add(section)
        db.session.commit()

        flash(
            'Section added successfully!',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Error: {str(e)}',
            'danger'
        )

    return redirect(url_for('admin.sections'))
@admin_bp.route('/sections/delete/<int:section_id>',
                methods=['POST'])
@login_required
@admin_required
def delete_section(section_id):

    try:
        section = Section.query.get_or_404(
            section_id
        )

        students_exist = Student.query.filter_by(
            section_id=section.id
        ).first()

        if students_exist:
            flash(
                'Cannot delete section. '
                'Students are assigned to it.',
                'danger'
            )

            return redirect(
                url_for('admin.sections')
            )

        db.session.delete(section)
        db.session.commit()

        flash(
            'Section deleted successfully!',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Error: {str(e)}',
            'danger'
        )

    return redirect(url_for('admin.sections'))
# ==========================
# Subject
# ==========================

@admin_bp.route('/subjects')
@login_required
@admin_required
def subjects():
    subjects_list = Subject.query.filter_by(is_active=True).all()
    return render_template('admin/subjects.html', subjects=subjects_list)

# ==========================
# Subject CRUD
# ==========================

@admin_bp.route('/subjects/add', methods=['POST'])
@login_required
@admin_required
def add_subject():
    try:
        code = request.form.get('code').strip()
        name = request.form.get('name').strip()
        credits = request.form.get('credits')
        subject_type = request.form.get('subject_type')

        existing = Subject.query.filter_by(code=code).first()

        if existing:

            if not existing.is_active:
                existing.name = name
                existing.credits = credits
                existing.subject_type = subject_type
                existing.is_active = True

                db.session.commit()

                flash(
                    'Inactive subject restored successfully!',
                    'success'
                )

                return redirect(url_for('admin.subjects'))

            flash('Subject already exists!', 'danger')
            return redirect(url_for('admin.subjects'))

        subject = Subject(
            code=code,
            name=name,
            credits=credits,
            subject_type=subject_type,
            is_active=True
        )

        db.session.add(subject)
        db.session.commit()

        flash('Subject added successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding subject: {str(e)}', 'danger')

    return redirect(url_for('admin.subjects'))


@admin_bp.route('/subjects/delete/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)

        subject.is_active = False

        db.session.commit()

        flash('Subject deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subject: {str(e)}', 'danger')

    return redirect(url_for('admin.subjects'))

# ==========================
# Teachers
# ==========================

@admin_bp.route('/teachers')
@login_required
@admin_required
def teachers():
    teachers_list = User.query.filter_by(role='teacher',is_active=True).all()
    return render_template('admin/teachers.html', teachers=teachers_list)

# ==========================
# Teacher CRUD
# ==========================

@admin_bp.route('/teachers/add', methods=['POST'])
@login_required
@admin_required
def add_teacher():
    try:
        full_name = request.form.get('full_name').strip()
        email = request.form.get('email').strip().lower()
        phone = request.form.get('phone')
        password = request.form.get('password')

        existing = User.query.filter_by(email=email).first()

        if existing:

            if not existing.is_active:
                existing.full_name = full_name
                existing.phone = phone
                existing.role = 'teacher'
                existing.is_active = True
                existing.set_password(password)

                db.session.commit()

                flash(
                    'Inactive teacher restored!',
                    'success'
                )

                return redirect(url_for('admin.teachers'))

            flash('Teacher already exists!', 'danger')
            return redirect(url_for('admin.teachers'))

        teacher = User(
            full_name=full_name,
            email=email,
            phone=phone,
            role='teacher',
            is_active=True
        )

        teacher.set_password(password)

        db.session.add(teacher)
        db.session.commit()

        flash('Teacher added successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding teacher: {str(e)}', 'danger')

    return redirect(url_for('admin.teachers'))


@admin_bp.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
@login_required
@admin_required
def delete_teacher(teacher_id):
    try:
        teacher = User.query.get_or_404(teacher_id)

        teacher.is_active = False

        db.session.commit()

        flash('Teacher deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting teacher: {str(e)}', 'danger')

    return redirect(url_for('admin.teachers'))

# ==========================
# Assignments
# ==========================

@admin_bp.route('/assignments')
@login_required
@admin_required
def assignments():
    assignments_list = SectionSubject.query.all()

    teachers = User.query.filter_by(
        role='teacher',
        is_active=True
    ).all()

    subjects = Subject.query.filter_by(
        is_active=True
    ).all()

    sections = Section.query.filter_by(
        is_active=True
    ).all()

    return render_template(
        'admin/assignments.html',
        assignments=assignments_list,
        teachers=teachers,
        subjects=subjects,
        sections=sections
    )
@admin_bp.route('/assignments/add', methods=['POST'])
@login_required
@admin_required
def add_assignment():

    teacher_id = request.form.get('teacher_id')
    subject_id = request.form.get('subject_id')
    section_id = request.form.get('section_id')

    exists = SectionSubject.query.filter_by(
        teacher_id=teacher_id,
        subject_id=subject_id,
        section_id=section_id
    ).first()

    if exists:
        flash('Assignment already exists!', 'danger')
        return redirect(url_for('admin.assignments'))

    assignment = SectionSubject(
        teacher_id=teacher_id,
        subject_id=subject_id,
        section_id=section_id
    )

    db.session.add(assignment)
    db.session.commit()

    flash('Teacher assigned successfully!', 'success')

    return redirect(url_for('admin.assignments'))


@admin_bp.route('/assignments/delete/<int:assignment_id>',
                methods=['POST'])
@login_required
@admin_required
def delete_assignment(assignment_id):

    assignment = SectionSubject.query.get_or_404(
        assignment_id
    )

    db.session.delete(assignment)
    db.session.commit()

    flash(
        'Assignment removed successfully!',
        'success'
    )

    return redirect(url_for('admin.assignments'))

# ==========================
# Import
# ==========================

@admin_bp.route('/import')
@login_required
@admin_required
def bulk_import():
    return render_template('admin/bulk_import.html')

@admin_bp.route('/import/teachers', methods=['POST'])
@login_required
@admin_required
def import_teachers():

    try:
        file = request.files.get('teacher_file')

        if not file:
            flash('No file uploaded!', 'danger')
            return redirect(url_for('admin.bulk_import'))

        df = pd.read_excel(file)

        added = 0
        skipped = 0

        for _, row in df.iterrows():

            email = str(row['email']).strip().lower()

            existing = User.query.filter_by(
                email=email
            ).first()

            if existing:
                skipped += 1
                continue

            teacher = User(
                full_name=str(row['full_name']),
                email=email,
                phone=str(row['phone']),
                role='teacher',
                is_active=True
            )

            teacher.set_password(
                str(row['password'])
            )

            db.session.add(teacher)
            added += 1

        db.session.commit()

        flash(
            f'Teachers imported successfully! Added: {added}, Skipped: {skipped}',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Import failed: {str(e)}',
            'danger'
        )

    return redirect(url_for('admin.bulk_import'))

@admin_bp.route('/import/students', methods=['POST'])
@login_required
@admin_required
def import_students():

    try:
        file = request.files.get('student_file')

        if not file:
            flash('No file uploaded!', 'danger')
            return redirect(url_for('admin.bulk_import'))

        df = pd.read_excel(file)

        added = 0
        skipped = 0
        skip_reasons = []

        for row_idx, row in df.iterrows():

            email = str(row.get('email', '')).strip().lower()

            if not email or email == 'nan':
                skipped += 1
                skip_reasons.append(
                    f"Row {row_idx + 2}: Missing email"
                )
                continue

            existing_user = User.query.filter_by(
                email=email
            ).first()

            if existing_user:
                skipped += 1
                skip_reasons.append(
                    f"Row {row_idx + 2}: User already exists ({email})"
                )
                continue

            # Find department
            dept_code = str(
                row.get('department_code', '')
            ).strip().upper()

            department = Department.query.filter_by(
                code=dept_code,
                is_active=True
            ).first()

            if not department:
                # Also try case-insensitive match
                department = Department.query.filter(
                    Department.code.ilike(dept_code),
                    Department.is_active == True
                ).first()

            if not department:
                skipped += 1
                all_depts = [
                    d.code for d in
                    Department.query.filter_by(
                        is_active=True
                    ).all()
                ]
                skip_reasons.append(
                    f"Row {row_idx + 2}: Department "
                    f"'{dept_code}' not found. "
                    f"Available: {all_depts}"
                )
                continue

            # Semester + Section
            try:
                semester_number = int(
                    float(row['semester'])
                )
            except (ValueError, TypeError):
                skipped += 1
                skip_reasons.append(
                    f"Row {row_idx + 2}: Invalid "
                    f"semester value "
                    f"'{row.get('semester')}'"
                )
                continue

            section_name = str(
                row.get('section_name', '')
            ).strip().upper()

            if not section_name or section_name == 'NAN':
                skipped += 1
                skip_reasons.append(
                    f"Row {row_idx + 2}: Missing "
                    f"section_name"
                )
                continue

            section = Section.query.join(
                Semester
            ).join(
                Program
            ).filter(
                Semester.number == semester_number,
                Program.department_id == department.id,
                Section.name.ilike(section_name),
                Section.is_active == True
            ).first()

            if not section:
                # Show what sections DO exist
                available = Section.query.join(
                    Semester
                ).join(
                    Program
                ).filter(
                    Program.department_id == department.id
                ).all()

                avail_info = [
                    f"Sem {s.semester.number}/{s.name}"
                    for s in available
                ] if available else ['None']

                skipped += 1
                skip_reasons.append(
                    f"Row {row_idx + 2}: Section not "
                    f"found for Dept={department.code}, "
                    f"Sem={semester_number}, "
                    f"Section={section_name}. "
                    f"Available sections: {avail_info}"
                )
                continue

            # Create user account
            user = User(
                full_name=str(row['name']),
                email=email,
                phone=str(row.get('phone', '')),
                role='student',
                is_active=True
            )

            user.set_password(
                str(row.get('password', email))
            )

            db.session.add(user)
            db.session.flush()

            # Create student profile
            student = Student(
                user_id=user.id,
                name=str(row['name']),
                roll_number=str(row['roll_number']),
                registration_number=str(
                    row['registration_number']
                ),
                email=email,
                phone=str(row.get('phone', '')),
                section_id=section.id,
                department_id=department.id,
                is_active=True
            )

            db.session.add(student)
            added += 1

        db.session.commit()

        flash(
            f'Students imported successfully! '
            f'Added: {added}, '
            f'Skipped: {skipped}',
            'success'
        )

        # Show skip reasons so the admin can fix data
        if skip_reasons:
            # Show first 10 reasons to avoid flooding
            reasons_display = skip_reasons[:10]
            remaining = len(skip_reasons) - 10

            for reason in reasons_display:
                flash(reason, 'warning')

            if remaining > 0:
                flash(
                    f'...and {remaining} more '
                    f'skipped rows (check server '
                    f'logs for full details).',
                    'warning'
                )

            # Also print all to server log
            for reason in skip_reasons:
                print(f"[IMPORT SKIP] {reason}")

    except Exception as e:
        db.session.rollback()

        flash(
            f'Import failed: {str(e)}',
            'danger'
        )

    return redirect(url_for('admin.bulk_import'))
@admin_bp.route('/import/subjects', methods=['POST'])
@login_required
@admin_required
def import_subjects():

    try:
        file = request.files.get('subject_file')

        if not file:
            flash('No file uploaded!', 'danger')
            return redirect(url_for('admin.subjects'))

        df = pd.read_excel(file)

        added = 0
        skipped = 0

        for _, row in df.iterrows():

            code = str(row['code']).strip()

            existing = Subject.query.filter_by(
                code=code
            ).first()

            if existing:
                skipped += 1
                continue

            department = Department.query.filter_by(
                code=str(
                    row['department_code']
                ).strip(),
                is_active=True
            ).first()

            if not department:
                skipped += 1
                continue

            subject = Subject(
                code=code,
                name=str(row['name']),
                credits=int(row['credits']),
                subject_type=str(
                    row['subject_type']
                ).lower(),
                is_active=True
            )

            db.session.add(subject)
            added += 1

        db.session.commit()

        flash(
            f'Subjects imported! Added: {added}, Skipped: {skipped}',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Import failed: {str(e)}',
            'danger'
        )

    return redirect(url_for('admin.subjects'))