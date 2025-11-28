"""
Wildlife Detection Module
Supports both mock (simulated) and real (YOLOv8) detection modes
"""

import random
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Wildlife classes commonly found in African reserves
# Maps YOLO class names to our wildlife taxonomy
WILDLIFE_CLASSES = {
    'elephant': ['elephant'],
    'lion': ['lion'],
    'leopard': ['leopard'],
    'buffalo': ['buffalo', 'cape buffalo'],
    'giraffe': ['giraffe'],
    'zebra': ['zebra'],
    'rhinoceros': ['rhinoceros', 'rhino'],
    'hippopotamus': ['hippopotamus', 'hippo'],
    'cheetah': ['cheetah'],
    'hyena': ['hyena'],
    'wild dog': ['wild dog', 'african wild dog'],
    'antelope': ['antelope', 'impala', 'gazelle', 'kudu'],
    'wildebeest': ['wildebeest', 'gnu'],
    'deer': ['deer', 'axis deer'],
    'bear': ['bear'],
    'wolf': ['wolf'],
    'person': ['person', 'human'],  # For ranger detection
    'vehicle': ['car', 'truck', 'motorcycle'],
}

# Mock species with typical confidence ranges for testing
MOCK_SPECIES = {
    'elephant': (0.85, 0.98),
    'lion': (0.80, 0.95),
    'leopard': (0.75, 0.92),
    'buffalo': (0.82, 0.96),
    'giraffe': (0.88, 0.99),
}


class DetectionResult:
    """Represents a single detection result"""
    
    def __init__(self, species: str, confidence: float, latitude: float, 
                 longitude: float, image_path: str = None):
        self.species = species
        self.confidence = confidence
        self.latitude = latitude
        self.longitude = longitude
        self.image_path = image_path
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database/API"""
        return {
            'species': self.species,
            'confidence': self.confidence,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_path': self.image_path,
            'timestamp': self.timestamp.isoformat()
        }


class WildlifeDetector:
    """Base detector class with mock and real implementations"""
    
    def __init__(self, use_mock: bool = True, model_path: str = None):
        """
        Initialize detector
        
        Args:
            use_mock: If True, use mock detector. If False, use YOLOv8
            model_path: Path to custom trained model (optional)
        """
        self.use_mock = use_mock
        self.model = None
        
        if not use_mock:
            self._load_yolov8_model(model_path)
    
    def _load_yolov8_model(self, model_path: Optional[str] = None):
        """Load YOLOv8 model"""
        try:
            from ultralytics import YOLO

            # model_path argument overrides environment/config
            env_model = os.environ.get('CUSTOM_MODEL_PATH')
            chosen = model_path or env_model

            if chosen and os.path.exists(chosen):
                logger.info(f"Loading custom model from {chosen}")
                self.model = YOLO(chosen)
            else:
                # If a model path is provided but doesn't exist, warn and fall back
                if chosen and not os.path.exists(chosen):
                    logger.warning(f"Requested model path does not exist: {chosen}. Falling back to pretrained yolov8m.pt")
                logger.info("Loading pre-trained YOLOv8 model (yolov8m.pt)")
                # ultralytics will download weights as needed
                self.model = YOLO('yolov8m.pt')
            
            logger.info("YOLOv8 model loaded successfully")
        except ImportError:
            logger.error("ultralytics not installed. Install with: pip install ultralytics")
            raise
        except Exception as e:
            logger.error(f"Error loading YOLOv8 model: {e}")
            raise
    
    def detect(self, image_path: str, latitude: float = None, 
               longitude: float = None, conf_threshold: float = 0.5) -> List[DetectionResult]:
        """
        Run detection on an image
        
        Args:
            image_path: Path to the image file
            latitude: GPS latitude (optional)
            longitude: GPS longitude (optional)
            conf_threshold: Confidence threshold (0-1)
        
        Returns:
            List of DetectionResult objects
        """
        if self.use_mock:
            return self._detect_mock(image_path, latitude, longitude, conf_threshold)
        else:
            return self._detect_yolov8(image_path, latitude, longitude, conf_threshold)
    
    def _detect_mock(self, image_path: str, latitude: float = None, 
                     longitude: float = None, conf_threshold: float = 0.5) -> List[DetectionResult]:
        """Simulate detections for testing"""
        
        # Default location (Masai Mara, Kenya)
        if latitude is None:
            latitude = -1.5 + random.uniform(-0.5, 0.5)
        if longitude is None:
            longitude = 35.3 + random.uniform(-0.5, 0.5)
        
        detections = []
        
        # Randomly decide if we detect something (70% chance)
        if random.random() < 0.7:
            # Pick 1-3 random wildlife
            num_detections = random.randint(1, 3)
            for _ in range(num_detections):
                species = random.choice(list(MOCK_SPECIES.keys()))
                min_conf, max_conf = MOCK_SPECIES[species]
                confidence = random.uniform(min_conf, max_conf)
                
                # Only include if above threshold
                if confidence >= conf_threshold:
                    detections.append(DetectionResult(
                        species=species,
                        confidence=confidence,
                        latitude=latitude + random.uniform(-0.01, 0.01),
                        longitude=longitude + random.uniform(-0.01, 0.01),
                        image_path=image_path
                    ))
        
        logger.info(f"Mock detection: Found {len(detections)} objects in {image_path}")
        return detections
    
    def _detect_yolov8(self, image_path: str, latitude: float = None, 
                       longitude: float = None, conf_threshold: float = 0.5) -> List[DetectionResult]:
        """Run real YOLOv8 detection with wildlife class filtering"""
        
        if self.model is None:
            raise ValueError("Model not loaded. Cannot run real detection.")
        
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Default location if not provided
        if latitude is None:
            latitude = -1.5
        if longitude is None:
            longitude = 35.3
        
        detections = []
        
        try:
            # Run YOLOv8 inference with confidence threshold
            results = self.model.predict(
                source=image_path, 
                conf=conf_threshold, 
                verbose=False,
                device=0  # Use GPU if available, CPU otherwise
            )
            
            # Process results
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    class_name = r.names[class_id].lower().strip()
                    confidence = float(box.conf[0])
                    
                    # Map YOLO class to our wildlife taxonomy
                    mapped_species = self._map_yolo_class(class_name)
                    
                    # Only include if it's a wildlife class we care about
                    if mapped_species:
                        detections.append(DetectionResult(
                            species=mapped_species,
                            confidence=confidence,
                            latitude=latitude + random.uniform(-0.001, 0.001),  # Add slight variation
                            longitude=longitude + random.uniform(-0.001, 0.001),
                            image_path=image_path
                        ))
            
            logger.info(f"YOLOv8 detection: Found {len(detections)} wildlife in {image_path}")
        
        except Exception as e:
            logger.error(f"Error during YOLOv8 detection: {e}")
            raise
        
        return detections
    
    def _map_yolo_class(self, class_name: str) -> Optional[str]:
        """
        Map YOLO class name to our wildlife taxonomy.
        
        Args:
            class_name: YOLO detected class name
        
        Returns:
            Mapped species name, or None if not a wildlife class
        """
        class_name_lower = class_name.lower().strip()
        
        # Check against our wildlife classes mapping
        for species, class_names in WILDLIFE_CLASSES.items():
            for cn in class_names:
                if cn in class_name_lower or class_name_lower in cn:
                    return species
        
        # Not found in our wildlife taxonomy
        return None
    
    def switch_mode(self, use_mock: bool):
        """Switch between mock and real detection"""
        self.use_mock = use_mock
        if not use_mock and self.model is None:
            self._load_yolov8_model()
        logger.info(f"Detection mode switched to: {'MOCK' if use_mock else 'REAL YOLOv8'}")


# Global detector instance
_detector_instance = None


def get_detector(use_mock: bool = True, model_path: str = None) -> WildlifeDetector:
    """Get or create detector instance"""
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = WildlifeDetector(use_mock=use_mock, model_path=model_path)
    
    return _detector_instance
