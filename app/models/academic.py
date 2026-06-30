"""Academic organizational models."""

from datetime import datetime
from app.extensions import db

class Department(db.Model):
    """Department model (e.g., Computer Science)."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    programs = db.relationship('Program', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    students = db.relationship('Student', backref='department', lazy='dynamic')

    def __repr__(self):
        return f"<Department {self.code}>"


class Program(db.Model):
    """Degree program (e.g., B.Tech Computer Science)."""
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    duration_years = db.Column(db.Integer, default=4, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    semesters = db.relationship('Semester', backref='program', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Program {self.code}>"


class Semester(db.Model):
    """Academic Semester."""
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(50), nullable=False)  # e.g., "Semester 1", "Semester 2"
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    sections = db.relationship('Section', backref='semester', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Semester {self.label} ({self.program.code if self.program else 'None'})>"


class Section(db.Model):
    """Academic Class Section (e.g., Section A, Section B)."""
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    name = db.Column(db.String(10), nullable=False)  # e.g., "A", "B"
    max_strength = db.Column(db.Integer, default=60, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    students = db.relationship('Student', backref='section', lazy='dynamic')
    section_subjects = db.relationship('SectionSubject', backref='section', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Section {self.name} - Sem {self.semester.number if self.semester else '?'}>"
