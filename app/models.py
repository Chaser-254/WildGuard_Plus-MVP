from app import db
from datetime import datetime

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    camera_id = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200))
    is_false_positive = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'species': self.species,
            'confidence': self.confidence,
            'camera_id': self.camera_id,
            'location': {
                'lat': self.latitude,
                'lng': self.longitude
            },
            'timestamp': self.timestamp.isoformat(),
            'image_path': self.image_path
        }

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'camera_id': self.camera_id,
            'name': self.name,
            'location': {
                'lat': self.latitude,
                'lng': self.longitude
            },
            'is_active': self.is_active,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)