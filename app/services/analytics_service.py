"""Analytics and Statistics service."""

from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.academic import Department, Section
from app.models.student import Student
from app.models.subject import SectionSubject, Subject
from app.models.attendance import Attendance

def get_dashboard_stats(user=None):
    """Get institution-wide or teacher-specific dashboard stats."""
    stats = {
        'total_students': 0,
        'total_teachers': 0,
        'total_departments': 0,
        'overall_attendance_pct': 100.0,
        'total_defaulters': 0,
        'active_classes': 0
    }

    if user and user.role == 'teacher':
        # Scope to teacher classes
        assignments = SectionSubject.query.filter_by(teacher_id=user.id).all()
        section_ids = [a.section_id for a in assignments]
        assignment_ids = [a.id for a in assignments]
        
        stats['active_classes'] = len(assignments)
        stats['total_students'] = Student.query.filter(Student.section_id.in_(section_ids) if section_ids else False).count()
        stats['total_teachers'] = 1  # Just themselves
        if section_ids:
            department_ids = db.session.query(Student.department_id).filter(Student.section_id.in_(section_ids)).all()
            stats['total_departments'] = len(set(d[0] for d in department_ids))
        else:
            stats['total_departments'] = 0
        # Calculate overall attendance for teacher's subjects
        if assignment_ids:
            total_records = Attendance.query.filter(Attendance.section_subject_id.in_(assignment_ids)).count()
            if total_records > 0:
                present_records = Attendance.query.filter(Attendance.section_subject_id.in_(assignment_ids), Attendance.status == 'present').count()
                stats['overall_attendance_pct'] = round((present_records / total_records) * 100, 2)
            else:
                stats['overall_attendance_pct'] = 100.0
                
            # Count defaulters in teacher's sections/subjects
            students = Student.query.filter(Student.section_id.in_(section_ids)).all()
            defaulters_count = 0
            for student in students:
                # check average across teacher's assigned subjects
                student_assigned_ss = [a.id for a in assignments if a.section_id == student.section_id]
                if student_assigned_ss:
                    total_s_rec = Attendance.query.filter(Attendance.student_id == student.id, Attendance.section_subject_id.in_(student_assigned_ss)).count()
                    if total_s_rec > 0:
                        pres_s_rec = Attendance.query.filter(Attendance.student_id == student.id, Attendance.section_subject_id.in_(student_assigned_ss), Attendance.status == 'present').count()
                        pct = (pres_s_rec / total_s_rec) * 100
                        if pct < 75.0:
                            defaulters_count += 1
            stats['total_defaulters'] = defaulters_count
            
    else:
        # Admin / Institution-wide stats
        stats['total_students'] = Student.query.count()
        stats['total_teachers'] = User.query.filter_by(role='teacher').count()
        stats['total_departments'] = Department.query.count()
        stats['active_classes'] = SectionSubject.query.count()
        
        total_records = Attendance.query.count()
        if total_records > 0:
            present_records = Attendance.query.filter_by(status='present').count()
            stats['overall_attendance_pct'] = round((present_records / total_records) * 100, 2)
        else:
            stats['overall_attendance_pct'] = 100.0

        # Calculate total defaulters overall
        students = Student.query.all()
        defaulters_count = 0
        for student in students:
            if student.is_defaulter(75):
                defaulters_count += 1
        stats['total_defaulters'] = defaulters_count

    return stats

def get_attendance_trend(days=30, teacher_id=None):
    """Retrieve daily attendance trends for the last N days."""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    # Query attendance counts grouped by date
    query = db.session.query(
        Attendance.date,
        func.count(Attendance.id).label('total'),
        func.sum(db.case((Attendance.status == 'present', 1), else_=0)).label('present')
    ).filter(Attendance.date.between(start_date, end_date))
    
    if teacher_id:
        assignments = SectionSubject.query.filter_by(teacher_id=teacher_id).all()
        assignment_ids = [a.id for a in assignments]
        if not assignment_ids:
            return []
        query = query.filter(Attendance.section_subject_id.in_(assignment_ids))
        
    results = query.group_by(Attendance.date).order_by(Attendance.date).all()
    
    trend = []
    for r in results:
        pct = round((r.present / r.total) * 100, 2) if r.total > 0 else 100.0
        trend.append({
            'date': r.date.strftime('%Y-%m-%d'),
            'percentage': pct
        })
    return trend

def get_monthly_attendance(year=None, teacher_id=None):
    """Get monthly attendance average."""
    if not year:
        year = datetime.utcnow().year
        
    query = db.session.query(
        func.strftime('%m', Attendance.date).label('month'),
        func.count(Attendance.id).label('total'),
        func.sum(db.case((Attendance.status == 'present', 1), else_=0)).label('present')
    ).filter(func.strftime('%Y', Attendance.date) == str(year))
    
    if teacher_id:
        assignments = SectionSubject.query.filter_by(teacher_id=teacher_id).all()
        assignment_ids = [a.id for a in assignments]
        if not assignment_ids:
            return []
        query = query.filter(Attendance.section_subject_id.in_(assignment_ids))
        
    results = query.group_by('month').order_by('month').all()
    
    months = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }
    
    monthly_data = []
    for r in results:
        pct = round((r.present / r.total) * 100, 2) if r.total > 0 else 100.0
        monthly_data.append({
            'month': months.get(r.month, r.month),
            'percentage': pct
        })
    return monthly_data

def get_class_wise_attendance(teacher_id=None):
    """Get attendance average per Class Section + Subject."""
    query = SectionSubject.query
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    
    assignments = query.all()
    class_wise = []
    
    for a in assignments:
        total_records = Attendance.query.filter_by(section_subject_id=a.id).count()
        if total_records > 0:
            present_records = Attendance.query.filter_by(section_subject_id=a.id, status='present').count()
            pct = round((present_records / total_records) * 100, 2)
        else:
            pct = 100.0
            
        class_name = f"{a.section.semester.program.code} S{a.section.semester.number}-{a.section.name} ({a.subject.code})"
        class_wise.append({
            'class_name': class_name,
            'percentage': pct
        })
        
    return class_wise

def get_defaulters_list(threshold=75, teacher_id=None):
    """Get list of students below threshold."""
    if teacher_id:
        assignments = SectionSubject.query.filter_by(teacher_id=teacher_id).all()
        section_ids = [a.section_id for a in assignments]
        students = Student.query.filter(Student.section_id.in_(section_ids) if section_ids else False).all()
    else:
        students = Student.query.all()
        
    defaulters = []
    for s in students:
        pct = s.get_attendance_percentage()
        if pct < threshold:
            defaulters.append({
                'id': s.id,
                'name': s.name,
                'roll_number': s.roll_number,
                'section': f"S{s.section.semester.number}-{s.section.name}",
                'program': s.section.semester.program.code,
                'percentage': pct
            })
    return defaulters

def get_student_dashboard_stats(student_id):
    """Get dashboard stats for a student."""
    student = Student.query.get(student_id)
    if not student:
        return {}
        
    # Get subjects in their section
    section_subjects = SectionSubject.query.filter_by(section_id=student.section_id).all()
    
    subjects_pct = []
    total_classes = 0
    total_present = 0
    
    for ss in section_subjects:
        q = Attendance.query.filter_by(student_id=student.id, section_subject_id=ss.id)
        ss_total = q.count()
        ss_present = q.filter_by(status='present').count()
        
        pct = round((ss_present / ss_total) * 100, 2) if ss_total > 0 else 100.0
        
        subjects_pct.append({
            'subject_name': ss.subject.name,
            'subject_code': ss.subject.code,
            'percentage': pct,
            'present': ss_present,
            'total': ss_total
        })
        
        total_classes += ss_total
        total_present += ss_present
        
    overall_pct = round((total_present / total_classes) * 100, 2) if total_classes > 0 else 100.0
    
    return {
        'overall_pct': overall_pct,
        'total_classes': total_classes,
        'total_present': total_present,
        'total_absent': total_classes - total_present,
        'subjects': subjects_pct,
        'is_defaulter': overall_pct < 75.0
    }
