"""Notification services."""

from app.extensions import db
from app.models.notification import Notification

def create_notification(user_id, title, message, notification_type='info', link=None):
    """Create a new notification for a user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
    db.session.add(notif)
    db.session.commit()
    return notif

def get_user_notifications(user_id, unread_only=False, limit=20):
    """Retrieve notifications for a user."""
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    return query.order_by(Notification.created_at.desc()).limit(limit).all()

def mark_as_read(notification_id):
    """Mark a notification as read."""
    notif = Notification.query.get(notification_id)
    if notif:
        notif.is_read = True
        db.session.commit()
        return True
    return False

def mark_all_as_read(user_id):
    """Mark all notifications for a user as read."""
    Notification.query.filter_by(user_id=user_id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    return True

def get_unread_count(user_id):
    """Get the count of unread notifications for a user."""
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()
