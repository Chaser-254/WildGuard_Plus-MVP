from app import db
from datetime import datetime


class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    detection_id = db.Column(db.Integer, db.ForeignKey('detections.id'), nullable=False)
    alert_type = db.Column(db.String(50), default='detection')  # 'detection', 'manual', etc.
    message = db.Column(db.Text)
    recipients = db.Column(db.String(500))  # comma-separated phone numbers or emails
    sms_sent = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'detection_id': self.detection_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'recipients': self.recipients,
            'sms_sent': self.sms_sent,
            'email_sent': self.email_sent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
