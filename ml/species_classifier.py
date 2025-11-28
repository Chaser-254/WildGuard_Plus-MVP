"""
Species Classifier for Wildlife Detection

Maps detected objects to wildlife species and assigns confidence scores.
In mock mode, generates random detections of common African wildlife.
In YOLOv8 mode, maps YOLO class IDs to species names.
"""

import random
from typing import Dict, List, Tuple


class SpeciesClassifier:
    """Classify detected animals into specific species."""
    
    # Wildlife species commonly found in African reserves
    WILDLIFE_SPECIES = {
        'elephant': {'common_names': ['elephant', 'loxodonta'], 'threat_level': 'medium'},
        'lion': {'common_names': ['lion', 'panthera leo'], 'threat_level': 'high'},
        'buffalo': {'common_names': ['buffalo', 'cape buffalo', 'syncerus'], 'threat_level': 'high'},
        'leopard': {'common_names': ['leopard', 'panthera pardus'], 'threat_level': 'high'},
        'zebra': {'common_names': ['zebra', 'equus'], 'threat_level': 'low'},
        'giraffe': {'common_names': ['giraffe', 'giraffa'], 'threat_level': 'low'},
        'hippo': {'common_names': ['hippo', 'hippopotamus'], 'threat_level': 'high'},
        'rhino': {'common_names': ['rhino', 'rhinoceros'], 'threat_level': 'high'},
        'wildebeest': {'common_names': ['wildebeest', 'gnu', 'connochaetes'], 'threat_level': 'low'},
        'antelope': {'common_names': ['antelope', 'impala', 'gazelle'], 'threat_level': 'low'},
        'cheetah': {'common_names': ['cheetah', 'acinonyx'], 'threat_level': 'high'},
        'hyena': {'common_names': ['hyena', 'crocuta'], 'threat_level': 'medium'},
        'warthog': {'common_names': ['warthog', 'phacochoerus'], 'threat_level': 'low'},
        'crocodile': {'common_names': ['crocodile', 'crocodylus'], 'threat_level': 'high'},
    }
    
    # YOLO class mappings (for future YOLOv8 integration)
    YOLO_CLASS_MAPPING = {
        # These map YOLO class IDs to species
        # We'll update this when we integrate real YOLOv8
        0: 'person',
        1: 'elephant',
        2: 'lion',
        3: 'buffalo',
        # ... more mappings
    }
    
    def __init__(self, mode: str = 'mock'):
        """
        Initialize the classifier.
        
        Args:
            mode: 'mock' for testing, 'yolo' for real YOLOv8 detections
        """
        self.mode = mode
    
    def classify_mock(self, seed: int = None) -> Tuple[str, float]:
        """
        Generate a mock wildlife detection for testing.
        
        Returns:
            (species_name, confidence_score)
        """
        if seed:
            random.seed(seed)
        
        species_list = list(self.WILDLIFE_SPECIES.keys())
        species = random.choice(species_list)
        confidence = round(random.uniform(0.75, 0.99), 2)  # 75-99% confidence
        
        return species, confidence
    
    def classify_yolo(self, class_id: int, class_name: str, confidence: float) -> Tuple[str, float]:
        """
        Map YOLO detection to a wildlife species.
        
        Args:
            class_id: YOLO class ID
            class_name: YOLO class name (e.g., 'elephant')
            confidence: YOLO confidence score (0-1)
        
        Returns:
            (species_name, confidence_score)
        """
        # First try to map by class name to our species
        class_name_lower = class_name.lower()
        for species, info in self.WILDLIFE_SPECIES.items():
            if class_name_lower in info['common_names']:
                return species, round(confidence, 2)
        
        # If not found, return the class name as-is
        return class_name_lower, round(confidence, 2)
    
    def classify_from_detection(self, detection: Dict) -> Dict:
        """
        Enhance a detection with species classification.
        
        Args:
            detection: Detection dict with 'class_id', 'class_name', 'confidence'
        
        Returns:
            Enhanced detection dict with 'species', 'threat_level'
        """
        if self.mode == 'yolo':
            species, conf = self.classify_yolo(
                detection.get('class_id', 0),
                detection.get('class_name', 'unknown'),
                detection.get('confidence', 0.5)
            )
        else:
            species, conf = self.classify_mock()
        
        threat_level = self.WILDLIFE_SPECIES.get(species, {}).get('threat_level', 'unknown')
        
        return {
            **detection,
            'species': species,
            'confidence': conf,
            'threat_level': threat_level
        }
    
    def get_species_list(self) -> List[str]:
        """Return list of all recognized wildlife species."""
        return list(self.WILDLIFE_SPECIES.keys())
    
    def get_threat_level(self, species: str) -> str:
        """Get threat level for a species."""
        return self.WILDLIFE_SPECIES.get(species, {}).get('threat_level', 'unknown')
