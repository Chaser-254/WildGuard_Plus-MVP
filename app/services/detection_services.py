"""
Enhanced Detection Service - Integrates ML detector with Flask app
Supports both mock (simulated) and real (YOLOv8) detection modes
"""

import os
from typing import List, Dict, Tuple
from app.models import Detection
from app.models.alert import Alert
from app import db
from ml.detector import get_detector
from ml.species_classifier import SpeciesClassifier
from config.detection_config import DETECTION_MODE, ALERT_THRESHOLD
import logging

logger = logging.getLogger(__name__)


class DetectionService:
    """Service to handle wildlife detection and storage"""
    
    def __init__(self, use_mock: bool = None, model_path: str = None):
        """
        Initialize detection service
        
        Args:
            use_mock: If None, reads from DETECTION_MODE config
            model_path: Path to custom model (optional)
        """
        # Use config if use_mock not specified
        if use_mock is None:
            use_mock = DETECTION_MODE == 'mock'
        
        self.detector = get_detector(use_mock=use_mock, model_path=model_path)
        self.classifier = SpeciesClassifier(mode='mock' if use_mock else 'yolo')
        self.use_mock = use_mock
        self.cameras = {
            'cam_001': {'lat': -1.9441, 'lng': 30.0619, 'name': 'Main Waterhole'},
            'cam_002': {'lat': -1.9500, 'lng': 30.0700, 'name': 'Northern Corridor'},
            'cam_003': {'lat': -1.9300, 'lng': 30.0500, 'name': 'Southern Border'}
        }
        
        logger.info(f"Detection Service initialized in {'MOCK' if use_mock else 'YOLOV8'} mode")
    
    def process_image(self, image_path: str, latitude: float = None, 
                     longitude: float = None, conf_threshold: float = 0.5,
                     socketio = None, camera_id: str = None, alert_callback=None) -> Tuple[List[Detection], bool]:
        """
        Process an image and save detections to database
        
        Args:
            image_path: Path to the image file
            latitude: GPS latitude (optional, will use camera location if camera_id provided)
            longitude: GPS longitude (optional, will use camera location if camera_id provided)
            conf_threshold: Confidence threshold (default 0.5)
            socketio: SocketIO instance for real-time notifications
            camera_id: Camera identifier (optional)
            alert_callback: Function to call when detection found (for alerts)
        
        Returns:
            Tuple of (list of Detection objects, success flag)
        """
        try:
            # Use camera location if camera_id provided
            if camera_id and camera_id in self.cameras:
                cam_info = self.cameras[camera_id]
                latitude = latitude or cam_info['lat']
                longitude = longitude or cam_info['lng']
            
            # Run detection
            detection_results = self.detector.detect(
                image_path=image_path,
                latitude=latitude,
                longitude=longitude,
                conf_threshold=conf_threshold
            )
            
            # Save detections to database and trigger alerts
            saved_detections = []
            for result in detection_results:
                # Classify species with confidence
                species_info = self.classifier.classify_from_detection({
                    'class_name': result.species,
                    'confidence': result.confidence
                })
                
                detection = Detection(
                    species=species_info['species'],
                    confidence=species_info['confidence'],
                    latitude=result.latitude,
                    longitude=result.longitude,
                    image_path=result.image_path,
                    camera_id=camera_id
                )
                db.session.add(detection)
                saved_detections.append(detection)
            
            db.session.commit()
            
            # Trigger alerts for high-confidence detections
            if alert_callback:
                for detection in saved_detections:
                    if detection.confidence >= ALERT_THRESHOLD:  # Use config threshold
                        alert_callback(detection)
            
            # Emit real-time notifications
            if socketio and saved_detections:
                for detection in saved_detections:
                    socketio.emit('new_detection', detection.to_dict(), namespace='/')
                logger.info(f"Emitted {len(saved_detections)} detection notifications")
            
            logger.info(f"Successfully processed {image_path}: {len(saved_detections)} detections")
            return saved_detections, True
        
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            db.session.rollback()
            return [], False
    
    def get_stats(self) -> Dict:
        """Get detection statistics"""
        total = Detection.query.count()
        verified = Detection.query.filter_by(is_verified=True).count()
        false_positives = Detection.query.filter_by(is_false_positive=True).count()
        
        species_counts = db.session.query(
            Detection.species, 
            db.func.count(Detection.id).label('count')
        ).group_by(Detection.species).all()
        
        return {
            'total_detections': total,
            'verified': verified,
            'false_positives': false_positives,
            'species': {s: c for s, c in species_counts}
        }
    
    def switch_mode(self, use_mock: bool):
        """Switch between mock and real detection"""
        self.detector.switch_mode(use_mock)


# Global service instance
_service_instance = None


def get_detection_service(use_mock: bool = True, model_path: str = None) -> DetectionService:
    """Get or create detection service instance"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = DetectionService(use_mock=use_mock, model_path=model_path)
    
    return _service_instance


# Default instance for backward compatibility
detection_service = get_detection_service(use_mock=True)