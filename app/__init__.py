"""Application factory."""

import os
from datetime import datetime
from flask import Flask, render_template
from app.config import config
from app.extensions import db, login_manager, csrf
from app.services.notification_service import get_unread_count
from app.utils.helpers import get_greeting

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Determine config name
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Load configuration
    app.config.from_object(config[config_name])

    # Ensure instance, uploads and exports folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, app.config['EXPORT_FOLDER']), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.teacher import teacher_bp
    from app.blueprints.student_bp import student_bp
    from app.blueprints.attendance import attendance_bp
    from app.blueprints.students import students_bp
    from app.blueprints.analytics import analytics_bp
    from app.blueprints.reports import reports_bp
    from app.blueprints.settings import settings_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    
    # Exempt API from CSRF for easy AJAX communication
    csrf.exempt(api_bp)
    app.register_blueprint(api_bp)

    # Public landing page route
    @app.route('/')
    def landing():
        """Render public landing page."""
        return render_template('landing.html')

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    # Template Context Processors
    @app.context_processor
    def inject_globals():
        """Inject useful variables into all templates."""
        from flask_login import current_user
        unread_notif_count = 0
        if current_user.is_authenticated:
            unread_notif_count = get_unread_count(current_user.id)
            
        return {
            'now': datetime.utcnow(),
            'get_greeting': get_greeting,
            'unread_notification_count': unread_notif_count
        }

    # Recreate tables in development mode if needed
    with app.app_context():
        db.create_all()

    return app
