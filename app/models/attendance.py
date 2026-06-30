"""Attendance records model."""

from datetime import datetime
from sqlalchemy import UniqueConstraint
from app.extensions import db

class Attendance(db.Model):
    """Attendance record for a student on a specific date for a specific class/subject."""
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    section_subject_id = db.Column(db.Integer, db.ForeignKey('section_subjects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False, default='present') # 'present', 'absent'
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    marked_by_user = db.relationship('User', backref=db.backref('marked_attendances', lazy='dynamic'), foreign_keys=[marked_by])

    __table_args__ = (
        UniqueConstraint('student_id', 'section_subject_id', 'date', name='uq_student_subject_date'),
    )

    def __repr__(self):
        return f"<Attendance Student:{self.student_id} Date:{self.date} Status:{self.status}>"
