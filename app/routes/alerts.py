from flask import Blueprint, request, jsonify
from app import db
from app.models import Detection
from app.services.notification_services import send_notifications

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alert', methods=['POST'])
def receive_alert():
    try:
        data = request.json
        
        # Create new detection
        detection = Detection(
            species=data.get('species', 'elephant'),
            confidence=data.get('confidence', 0.0),
            camera_id=data.get('camera_id', 'unknown'),
            latitude=data['location']['lat'],
            longitude=data['location']['lng'],
            image_path=data.get('image_path')
        )
        
        db.session.add(detection)
        db.session.commit()
        
        # Send notifications
        send_notifications(detection)
        
        return jsonify({
            'status': 'success',
            'message': 'Alert processed',
            'detection_id': detection.id
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400