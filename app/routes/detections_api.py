"""
Detection System API Routes

Provides endpoints for:
- Uploading images and running detections
- Viewing detection statistics and history
- Managing cameras and streams
- Monitoring system status
"""

from flask import Blueprint, request, jsonify, render_template
from app.models import Detection, Camera, Subscriber, Alert
from app.models.alert import Alert
from app import db, socketio
from app.services.detection_services import get_detection_service
from app.services.notification_services import send_notifications
import os
import logging

logger = logging.getLogger(__name__)

detections_api_bp = Blueprint('detections_api', __name__, url_prefix='/api/detections')

# Get detection service instance
detection_service = get_detection_service(use_mock=True)


@detections_api_bp.route('/upload', methods=['POST'])
def upload_detection():
    """
    Upload an image and run detection.
    
    Form data:
        - file: Image file
        - latitude: GPS latitude (optional)
        - longitude: GPS longitude (optional)
        - camera_id: Camera identifier (optional)
    """
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Save uploaded file
        upload_folder = os.path.join('app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Get location data
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        camera_id = request.form.get('camera_id')
        
        # Run detection
        detections, success = detection_service.process_image(
            image_path=filepath,
            latitude=latitude,
            longitude=longitude,
            camera_id=camera_id,
            socketio=socketio
        )
        
        if not success:
            return jsonify({'status': 'error', 'message': 'Detection failed'}), 500
        
        # Trigger alerts for high-confidence detections
        for detection in detections:
            if detection.confidence >= 0.8:
                send_notifications(detection)
        
        return jsonify({
            'status': 'success',
            'detections': [d.to_dict() for d in detections],
            'count': len(detections)
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading detection: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@detections_api_bp.route('/recent', methods=['GET'])
def get_recent_detections():
    """Get recent detections (last 100)"""
    try:
        limit = request.args.get('limit', 100, type=int)
        detections = Detection.query\
            .filter_by(is_false_positive=False)\
            .order_by(Detection.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            'status': 'success',
            'detections': [d.to_dict() for d in detections],
            'count': len(detections)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching recent detections: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@detections_api_bp.route('/stats', methods=['GET'])
def get_detection_stats():
    """Get detection statistics"""
    try:
        stats = detection_service.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@detections_api_bp.route('/by-species/<species>', methods=['GET'])
def get_detections_by_species(species: str):
    """Get detections for a specific species"""
    try:
        limit = request.args.get('limit', 50, type=int)
        detections = Detection.query\
            .filter_by(species=species, is_false_positive=False)\
            .order_by(Detection.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            'status': 'success',
            'species': species,
            'detections': [d.to_dict() for d in detections],
            'count': len(detections)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching detections for {species}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@detections_api_bp.route('/<int:detection_id>', methods=['GET'])
def get_detection(detection_id: int):
    """Get details of a specific detection"""
    try:
        detection = Detection.query.get(detection_id)
        if not detection:
            return jsonify({'status': 'error', 'message': 'Detection not found'}), 404
        
        return jsonify({
            'status': 'success',
            'detection': detection.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching detection {detection_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@detections_api_bp.route('/<int:detection_id>/verify', methods=['POST'])
def verify_detection(detection_id: int):
    """Mark a detection as verified"""
    try:
        detection = Detection.query.get(detection_id)
        if not detection:
            return jsonify({'status': 'error', 'message': 'Detection not found'}), 404
        
        detection.is_verified = True
        db.session.commit()
        
        # Emit update event
        socketio.emit('detection_verified', {'detection_id': detection_id}, namespace='/')
        
        return jsonify({
            'status': 'success',
            'detection': detection.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error verifying detection {detection_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@detections_api_bp.route('/<int:detection_id>/false-positive', methods=['POST'])
def mark_false_positive(detection_id: int):
    """Mark a detection as false positive"""
    try:
        detection = Detection.query.get(detection_id)
        if not detection:
            return jsonify({'status': 'error', 'message': 'Detection not found'}), 404
        
        detection.is_false_positive = True
        db.session.commit()
        
        # Emit update event
        socketio.emit('false_positive_marked', {'detection_id': detection_id}, namespace='/')
        
        return jsonify({
            'status': 'success',
            'detection': detection.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error marking detection {detection_id} as false positive: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Camera endpoints
@detections_api_bp.route('/cameras', methods=['GET'])
def list_cameras():
    """List all cameras"""
    try:
        cameras = Camera.query.all()
        return jsonify({
            'status': 'success',
            'cameras': [c.to_dict() if hasattr(c, 'to_dict') else {
                'id': c.id,
                'camera_id': c.camera_id,
                'name': c.name,
                'latitude': c.latitude,
                'longitude': c.longitude,
                'is_active': c.is_active,
                'last_seen': c.last_seen.isoformat() if c.last_seen else None
            } for c in cameras],
            'count': len(cameras)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching cameras: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@detections_api_bp.route('/cameras', methods=['POST'])
def add_camera():
    """Add a new camera"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['camera_id', 'name', 'latitude', 'longitude']
        if not all(k in data for k in required):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Check if camera already exists
        existing = Camera.query.filter_by(camera_id=data['camera_id']).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'Camera already exists'}), 409
        
        camera = Camera(
            camera_id=data['camera_id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(camera)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f"Camera {data['camera_id']} added successfully",
            'camera': {
                'id': camera.id,
                'camera_id': camera.camera_id,
                'name': camera.name,
                'latitude': camera.latitude,
                'longitude': camera.longitude,
                'is_active': camera.is_active
            }
        }), 201
    
    except Exception as e:
        logger.error(f"Error adding camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Dashboard summary endpoint
@detections_api_bp.route('/dashboard-summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary with all key statistics"""
    try:
        total_detections = Detection.query.count()
        verified_detections = Detection.query.filter_by(is_verified=True).count()
        high_confidence = Detection.query.filter(Detection.confidence >= 0.9).count()
        
        # Get top species
        top_species = db.session.query(
            Detection.species,
            db.func.count(Detection.id).label('count')
        ).filter_by(is_false_positive=False)\
         .group_by(Detection.species)\
         .order_by(db.func.count(Detection.id).desc())\
         .limit(5).all()
        
        # Get recent detections
        recent = Detection.query\
            .filter_by(is_false_positive=False)\
            .order_by(Detection.timestamp.desc())\
            .limit(10).all()
        
        # Get active cameras
        active_cameras = Camera.query.filter_by(is_active=True).count()
        
        return jsonify({
            'status': 'success',
            'summary': {
                'total_detections': total_detections,
                'verified_detections': verified_detections,
                'high_confidence_count': high_confidence,
                'active_cameras': active_cameras,
                'top_species': [{'species': s, 'count': c} for s, c in top_species],
                'recent_detections': [d.to_dict() for d in recent]
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
