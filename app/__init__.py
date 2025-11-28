from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
socketio = SocketIO()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        app.config.from_object('config.development.Config')
    else:
        app.config.from_object('config.default.Config')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    socketio.init_app(app)
    
    # Import models here to avoid circular imports
    from app.models.detection import Detection
    from app.models import Camera, Subscriber
    
    # Register blueprints
    from app.routes.detections import detections_bp, register_socket_events
    from app.routes.detections_api import detections_api_bp
    from app.routes.management import management_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.pages import pages_bp
    from app.routes.config import config_bp
    from app.routes.alerts import alerts_bp
    from app.routes.streams import streams_bp
    
    app.register_blueprint(dashboard_bp)  # dashboard has '/' route for root
    app.register_blueprint(detections_bp, url_prefix='/api')
    app.register_blueprint(detections_api_bp)  # includes /api/detections prefix
    app.register_blueprint(management_bp)  # includes /api/system prefix
    app.register_blueprint(alerts_bp, url_prefix='/api')
    app.register_blueprint(streams_bp, url_prefix='/api')
    app.register_blueprint(config_bp, url_prefix='/api')
    app.register_blueprint(pages_bp)

    #creating all database tables
    with app.app_context():
        db.create_all()

    # Register socket.io events
    register_socket_events(socketio)

    # Register custom CLI commands (e.g. `flask clear-detections`)
    try:
        from app import cli as app_cli
        app_cli.register_commands(app)
    except Exception:
        # If CLI registration fails, continue; command won't be available.
        pass

    # Create uploads directory
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    
    return app