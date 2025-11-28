from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit
from app import socketio
from app import db
from app.models import Detection
from app.services.sms_service import SMSService
from app.services.detection_services import get_detection_service
from datetime import datetime
import os
from werkzeug.utils import secure_filename

detections_bp = Blueprint('detections', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def register_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        current_app.logger.info('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        current_app.logger.info('Client disconnected')

@detections_bp.route('/detections', methods=['GET', 'POST'])
def handle_detections():
    if request.method == 'POST':
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join('uploads', filename)
                file.save(os.path.join(current_app.static_folder, image_path))
                
                # Get detection service (uses mock mode by default for MVP)
                detection_service = get_detection_service(use_mock=True)
                
                # Extract location from form
                latitude = request.form.get('latitude', type=float)
                longitude = request.form.get('longitude', type=float)
                conf_threshold = request.form.get('conf_threshold', 0.5, type=float)
                
                # Run detection on the uploaded image
                detected_objects, success = detection_service.process_image(
                    image_path=os.path.join(current_app.static_folder, image_path),
                    latitude=latitude,
                    longitude=longitude,
                    conf_threshold=conf_threshold,
                    socketio=None  # Can pass socketio instance for real-time updates
                )
                
                if success:
                    return jsonify({
                        'status': 'success',
                        'message': f'Image processed. Found {len(detected_objects)} detections.',
                        'detections': [d.to_dict() for d in detected_objects],
                        'image_path': image_path
                    }), 201
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Failed to process image'
                    }), 400
        
        # Manual detection (from form data)
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location = request.form.get('location')
        
        # Parse location string if provided (format: "lat,lng")
        if location and not latitude:
            try:
                lat_str, lng_str = location.split(',')
                latitude = float(lat_str.strip())
                longitude = float(lng_str.strip())
            except (ValueError, AttributeError):
                latitude = -1.5
                longitude = 35.3
        
        latitude = float(latitude) if latitude else -1.5
        longitude = float(longitude) if longitude else 35.3
        
        detection = Detection(
            species=request.form.get('species'),
            confidence=float(request.form.get('confidence', 0)),
            latitude=latitude,
            longitude=longitude,
            image_path=image_path
        )
        
        db.session.add(detection)
        db.session.commit()
        
        # Use the application's Socket.IO instance to emit (safe outside socket handlers)
        socketio.emit('new_detection', detection.to_dict(), namespace='/')
        
        return jsonify(detection.to_dict()), 201
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Detection.query.order_by(Detection.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [d.to_dict() for d in pagination.items],
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'pages': pagination.pages
    })

@detections_bp.route('/detections/<int:detection_id>', methods=['GET', 'PUT'])
def handle_detection(detection_id):
    detection = Detection.query.get_or_404(detection_id)
    
    if request.method == 'PUT':
        data = request.get_json()
        detection.is_verified = data.get('is_verified', detection.is_verified)
        db.session.commit()
        socketio.emit('detection_updated', detection.to_dict(), namespace='/')
    
    return jsonify(detection.to_dict())


@detections_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get detection statistics"""
    detection_service = get_detection_service(use_mock=True)
    stats = detection_service.get_stats()
    return jsonify(stats)


@detections_bp.route('/mode', methods=['GET', 'POST'])
def detection_mode():
    """Get or switch detection mode (mock/real)"""
    if request.method == 'POST':
        data = request.get_json()
        use_mock = data.get('use_mock', True)
        detection_service = get_detection_service(use_mock=use_mock)
        detection_service.switch_mode(use_mock)
        
        mode = 'MOCK (Simulated)' if use_mock else 'REAL (YOLOv8)'
        return jsonify({
            'status': 'success',
            'message': f'Detection mode switched to {mode}',
            'use_mock': use_mock
        })
    
    # GET - return current mode
    detection_service = get_detection_service(use_mock=True)
    use_mock = detection_service.detector.use_mock
    mode = 'MOCK (Simulated)' if use_mock else 'REAL (YOLOv8)'
    
    return jsonify({
        'use_mock': use_mock,
        'mode': mode
    })