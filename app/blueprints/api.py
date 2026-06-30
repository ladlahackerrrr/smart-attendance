"""JSON API blueprint for AJAX requests."""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.academic import Department, Program, Semester, Section
from app.models.subject import SectionSubject
from app.models.student import Student
from app.services.attendance_service import save_attendance, get_students_for_marking
from app.services.notification_service import get_user_notifications, mark_as_read, mark_all_as_read

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/departments')
@login_required
def get_departments():
    depts = Department.query.filter_by(is_active=True).all()
    return jsonify([{'id': d.id, 'name': d.name, 'code': d.code} for d in depts])

@api_bp.route('/programs/<int:dept_id>')
@login_required
def get_programs(dept_id):
    progs = Program.query.filter_by(department_id=dept_id, is_active=True).all()
    return jsonify([{'id': p.id, 'name': p.name, 'code': p.code} for p in progs])

@api_bp.route('/semesters/<int:prog_id>')
@login_required
def get_semesters(prog_id):
    sems = Semester.query.filter_by(program_id=prog_id, is_active=True).all()
    return jsonify([{'id': s.id, 'number': s.number, 'label': s.label} for s in sems])

@api_bp.route('/sections/<int:sem_id>')
@login_required
def get_sections(sem_id):
    secs = Section.query.filter_by(semester_id=sem_id, is_active=True).all()
    return jsonify([{'id': s.id, 'name': s.name, 'max_strength': s.max_strength} for s in secs])

@api_bp.route('/subjects/<int:section_id>')
@login_required
def get_subjects(section_id):
    # Query SectionSubject mapping to get subjects assigned to this section
    # If teacher, only load their subjects for this section
    query = SectionSubject.query.filter_by(section_id=section_id)
    if current_user.role == 'teacher':
        query = query.filter_by(teacher_id=current_user.id)
    
    ss_assignments = query.all()
    return jsonify([{
        'section_subject_id': ss.id,
        'subject_id': ss.subject.id,
        'name': ss.subject.name,
        'code': ss.subject.code,
        'teacher_name': ss.teacher.full_name
    } for ss in ss_assignments])

@api_bp.route('/students/<int:section_id>')
@login_required
def get_students(section_id):
    # If marking attendance, we use get_students_for_marking which checks existing attendance
    section_subject_id = request.args.get('section_subject_id', type=int)
    date_val = request.args.get('date')
    
    if section_subject_id:
        students = get_students_for_marking(section_subject_id, date_val)
        return jsonify(students)
        
    students = Student.query.filter_by(section_id=section_id, is_active=True).all()
    return jsonify([{'id': s.id, 'name': s.name, 'roll_number': s.roll_number} for s in students])

@api_bp.route('/attendance/save', methods=['POST'])
@login_required
def save_class_attendance():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    section_subject_id = data.get('section_subject_id')
    date_val = data.get('date')
    records = data.get('records') # [{'student_id': 1, 'status': 'present'}]
    
    if not section_subject_id or not date_val or not records:
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Check permissions (teacher must be assigned, or admin)
    ss = SectionSubject.query.get(section_subject_id)
    if not ss:
        return jsonify({'error': 'Class assignment not found'}), 404
        
    if current_user.role == 'teacher' and ss.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized to mark attendance for this class'}), 403
        
    success = save_attendance(section_subject_id, date_val, records, current_user.id)
    if success:
        return jsonify({'message': 'Attendance saved successfully'}), 200
    return jsonify({'error': 'Failed to save attendance'}), 500

@api_bp.route('/notifications')
@login_required
def get_notifications():
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    notifs = get_user_notifications(current_user.id, unread_only=unread_only)
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        'link': n.link
    } for n in notifs])

@api_bp.route('/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    success = mark_as_read(notif_id)
    if success:
        return jsonify({'message': 'Notification marked as read'}), 200
    return jsonify({'error': 'Notification not found'}), 404

@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    mark_all_as_read(current_user.id)
    return jsonify({'message': 'All notifications marked as read'}), 200
