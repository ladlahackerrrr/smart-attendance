"""Student model."""

from datetime import datetime
from app.extensions import db


class Student(db.Model):
    """Student profile model."""
    __tablename__ = 'students'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )  # Linked User account

    name = db.Column(
        db.String(100),
        nullable=False
    )

    roll_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    registration_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    section_id = db.Column(
        db.Integer,
        db.ForeignKey('sections.id'),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey('departments.id'),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = db.relationship(
        'User',
        backref=db.backref(
            'student_profile',
            uselist=False
        )
    )

    attendances = db.relationship(
        'Attendance',
        backref='student',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def get_attendance_percentage(
        self,
        section_subject_id=None
    ):
        """Calculate attendance percentage."""

        from app.models.attendance import Attendance

        query = Attendance.query.filter_by(
            student_id=self.id
        )

        if section_subject_id:
            query = query.filter_by(
                section_subject_id=section_subject_id
            )

        total = query.count()

        if total == 0:
            return 0.0

        present = query.filter_by(
            status='present'
        ).count()

        return round(
            (present / total) * 100,
            2
        )

    def is_defaulter(
        self,
        threshold=75
    ):
        """Check if student's attendance falls below threshold."""
        return (
            self.get_attendance_percentage()
            < threshold
        )

    def __repr__(self):
        return (
            f"<Student "
            f"{self.roll_number} - "
            f"{self.name}>"
        )