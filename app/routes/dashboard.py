from flask import Blueprint, render_template, jsonify
from app.models import Detection, Camera

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/map-data')
def map_data():
    try:
        # Get recent detections
        detections = Detection.query.filter_by(is_false_positive=False)\
            .order_by(Detection.timestamp.desc())\
            .limit(100)\
            .all()
        
        # Get camera locations
        cameras = Camera.query.filter_by(is_active=True).all()
        
        return jsonify({
            'detections': [detection.to_dict() for detection in detections],
            'cameras': [camera.to_dict() for camera in cameras]
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400