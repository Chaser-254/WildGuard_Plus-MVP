from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        app.config.from_object('config.development.Config')
    else:
        app.config.from_object('config.default.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    
    # Register blueprints
    from app.routes.alerts import alerts_bp
    from app.routes.detections import detections_bp
    from app.routes.subscribers import subscribers_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.pages import pages_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerts_bp, url_prefix='/api')
    app.register_blueprint(detections_bp, url_prefix='/api')
    app.register_blueprint(subscribers_bp, url_prefix='/api')
    app.register_blueprint(pages_bp)
    
    return app