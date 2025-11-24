from flask import Blueprint, request, jsonify
from app.models import Detection

detections_bp = Blueprint('detections', __name__)

@detections_bp.route('/detections', methods=['GET'])
def get_detections():
    limit = request.args.get('limit', 50, type=int)
    detections = Detection.query.order_by(Detection.timestamp.desc()).limit(limit).all()
    
    return jsonify([detection.to_dict() for detection in detections])

@detections_bp.route('/detections/<int:detection_id>', methods=['GET'])
def get_detection(detection_id):
    detection = Detection.query.get_or_404(detection_id)
    return jsonify(detection.to_dict())