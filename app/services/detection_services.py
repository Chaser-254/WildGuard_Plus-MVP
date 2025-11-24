import cv2
import numpy as np
from datetime import datetime
import os

class DetectionService:
    def __init__(self):
        self.cameras = {
            'cam_001': {'lat': -1.9441, 'lng': 30.0619, 'name': 'Main Waterhole'},
            'cam_002': {'lat': -1.9500, 'lng': 30.0700, 'name': 'Northern Corridor'},
            'cam_003': {'lat': -1.9300, 'lng': 30.0500, 'name': 'Southern Border'}
        }
    
    def process_image(self, image_path, camera_id='cam_001'):
        """Process image and return detection results"""
        # For MVP, we'll use mock detection
        # Replace this with actual ML model inference
        
        # Simulate detection with 80% probability
        import random
        if random.random() > 0.2:  # 80% chance of detection for demo
            detection_data = {
                'species': 'elephant',
                'confidence': round(0.7 + random.random() * 0.3, 2),  # 0.7-1.0
                'camera_id': camera_id,
                'location': self.cameras.get(camera_id, self.cameras['cam_001']),
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path
            }
            return [detection_data]
        
        return []

detection_service = DetectionService()