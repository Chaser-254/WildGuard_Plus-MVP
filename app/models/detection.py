from app import db
from datetime import datetime

class Detection(db.Model):
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    camera_id = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
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
            # Include top-level latitude/longitude for clients that expect them
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_verified': self.is_verified,
            'timestamp': self.timestamp.isoformat(),
            'image_path': self.image_path
        }