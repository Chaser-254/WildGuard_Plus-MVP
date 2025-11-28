"""
System Management API Routes

Provides endpoints for:
- Switching detection modes (mock/YOLOv8)
- System status and configuration
- Model management
"""

from flask import Blueprint, request, jsonify
from app.services.detection_services import detection_service
import logging

logger = logging.getLogger(__name__)

management_bp = Blueprint('management', __name__, url_prefix='/api/system')


@management_bp.route('/status', methods=['GET'])
def system_status():
    """Get system status and current configuration"""
    try:
        detector = detection_service.detector
        
        return jsonify({
            'status': 'success',
            'system': {
                'detection_mode': 'MOCK' if detection_service.use_mock else 'YOLOV8',
                'detector_loaded': detector.model is not None if not detection_service.use_mock else True,
                'cameras_count': len(detection_service.cameras),
                'available_species': detector.classifier.get_species_list() if hasattr(detector, 'classifier') else []
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@management_bp.route('/detection-mode', methods=['GET'])
def get_detection_mode():
    """Get current detection mode"""
    try:
        return jsonify({
            'status': 'success',
            'mode': 'mock' if detection_service.use_mock else 'yolov8',
            'message': 'Using ' + ('mock detector (testing mode)' if detection_service.use_mock else 'real YOLOv8 model')
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting detection mode: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@management_bp.route('/detection-mode', methods=['POST'])
def set_detection_mode():
    """
    Switch detection mode between mock and yolov8
    
    JSON payload:
        {
            "mode": "mock" or "yolov8"
        }
    """
    try:
        data = request.get_json()
        mode = data.get('mode', '').lower()
        
        if mode not in ('mock', 'yolov8'):
            return jsonify({
                'status': 'error',
                'message': 'Invalid mode. Use "mock" or "yolov8"'
            }), 400
        
        use_mock = (mode == 'mock')
        
        # Switch mode
        detection_service.switch_mode(use_mock)
        
        # Reinitialize classifier
        from ml.species_classifier import SpeciesClassifier
        detection_service.classifier = SpeciesClassifier(mode='mock' if use_mock else 'yolo')
        
        return jsonify({
            'status': 'success',
            'message': f'Detection mode switched to {mode}',
            'mode': mode,
            'detector_status': 'MOCK' if use_mock else 'YOLOV8'
        }), 200
    
    except Exception as e:
        logger.error(f"Error switching detection mode: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@management_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """Get information about the loaded model"""
    try:
        if detection_service.use_mock:
            return jsonify({
                'status': 'success',
                'mode': 'mock',
                'model': {
                    'name': 'Mock Detector',
                    'type': 'Simulated',
                    'species_supported': detection_service.classifier.get_species_list(),
                    'gpu_enabled': False
                }
            }), 200
        
        else:
            detector = detection_service.detector
            model = detector.model
            
            if model is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Model not loaded'
                }), 400
            
            import torch
            
            return jsonify({
                'status': 'success',
                'mode': 'yolov8',
                'model': {
                    'name': model.model_name or 'YOLOv8',
                    'type': 'YOLOv8',
                    'device': str(model.device),
                    'gpu_enabled': torch.cuda.is_available(),
                    'gpu_device': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                    'species_supported': detection_service.classifier.get_species_list()
                }
            }), 200
    
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@management_bp.route('/species-list', methods=['GET'])
def get_species_list():
    """Get list of all supported wildlife species"""
    try:
        species_list = detection_service.classifier.get_species_list()
        
        # Get threat levels for each species
        species_with_threat = []
        for species in species_list:
            threat_level = detection_service.classifier.get_threat_level(species)
            species_with_threat.append({
                'name': species,
                'threat_level': threat_level
            })
        
        return jsonify({
            'status': 'success',
            'total_species': len(species_with_threat),
            'species': sorted(species_with_threat, key=lambda x: x['name'])
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting species list: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@management_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'WildGuard Detection System',
            'version': '1.0.0',
            'detection_mode': 'MOCK' if detection_service.use_mock else 'YOLOV8'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': str(e)
        }), 500
