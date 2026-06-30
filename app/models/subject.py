"""Subject and Teacher Assignment models."""

from datetime import datetime
from sqlalchemy import UniqueConstraint
from app.extensions import db

class Subject(db.Model):
    """Subject model (e.g., Data Structures, DBMS)."""
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, default=3, nullable=False)
    subject_type = db.Column(db.String(20), default='theory', nullable=False)  # 'theory', 'practical', 'elective'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    section_subjects = db.relationship('SectionSubject', backref='subject', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Subject {self.code}: {self.name}>"


class SectionSubject(db.Model):
    """Pivot table assigning Subjects to Sections, taught by a specific Teacher."""
    __tablename__ = 'section_subjects'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    # backref='teacher' created in User, but let's define it on this side or backref on User:
    teacher = db.relationship('User', backref=db.backref('teaching_assignments', cascade='all, delete-orphan'))
    attendances = db.relationship('Attendance', backref='section_subject', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        UniqueConstraint('section_id', 'subject_id', name='uq_section_subject'),
    )

    def __repr__(self):
        return f"<SectionSubject Section:{self.section_id} Subject:{self.subject_id} Teacher:{self.teacher_id}>"
