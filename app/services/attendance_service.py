"""Attendance management services."""

from datetime import datetime
from app.extensions import db
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.subject import SectionSubject

def get_students_for_marking(section_subject_id, date_val=None):
    """Retrieve students in a section and their attendance status for a date."""
    if not date_val:
        date_val = datetime.utcnow().date()
    elif isinstance(date_val, str):
        date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
        
    ss = SectionSubject.query.get(section_subject_id)
    if not ss:
        return []
        
    students = Student.query.filter_by(section_id=ss.section_id, is_active=True).all()
    results = []
    
    for s in students:
        att = Attendance.query.filter_by(
            student_id=s.id,
            section_subject_id=section_subject_id,
            date=date_val
        ).first()
        
        status = att.status if att else None
        results.append({
            'id': s.id,
            'name': s.name,
            'roll_number': s.roll_number,
            'status': status
        })
        
    return results

def save_attendance(section_subject_id, date_val, attendance_data, marked_by):
    """Save or update attendance for a class on a specific date.
    
    attendance_data is a list of dicts: [{'student_id': 1, 'status': 'present'}]
    """
    if isinstance(date_val, str):
        date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
        
    for item in attendance_data:
        student_id = int(item['student_id'])
        status = item['status']
        
        # Check if record already exists
        att = Attendance.query.filter_by(
            student_id=student_id,
            section_subject_id=section_subject_id,
            date=date_val
        ).first()
        
        if att:
            att.status = status
            att.marked_by = marked_by
            att.updated_at = datetime.utcnow()
        else:
            att = Attendance(
                student_id=student_id,
                section_subject_id=section_subject_id,
                date=date_val,
                status=status,
                marked_by=marked_by
            )
            db.session.add(att)
            
    db.session.commit()
    return True

def get_teacher_classes(teacher_id):
    """Get SectionSubjects assigned to a teacher."""
    return SectionSubject.query.filter_by(teacher_id=teacher_id).all()
