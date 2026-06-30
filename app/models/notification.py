"""Notification model."""

from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    """Notification model for user alerts, low attendance warnings, etc."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), default='info', nullable=False) # 'alert', 'info', 'warning', 'success'
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    link = db.Column(db.String(255), nullable=True) # Optional URL link to go to on click

    # Relationships
    user = db.relationship('User', backref=db.backref('notifications_list', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Notification {self.title} for User {self.user_id}>"
