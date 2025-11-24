import os

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///elephant_detections.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application Settings
    NOTIFICATION_COOLDOWN = int(os.environ.get('NOTIFICATION_COOLDOWN', 300))  # 5 minutes
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 0.7))
    
    # Camera Settings
    DEFAULT_CAMERAS = [
        {'id': 'cam_001', 'lat': -1.9441, 'lng': 30.0619, 'name': 'Main Waterhole'},
        {'id': 'cam_002', 'lat': -1.9500, 'lng': 30.0700, 'name': 'Northern Corridor'},
        {'id': 'cam_003', 'lat': -1.9300, 'lng': 30.0500, 'name': 'Southern Border'}
    ]