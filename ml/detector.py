import torch
import torchvision.transforms as T
import torchvision.models as models
from PIL import Image
import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElephantDetector:
    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold
        self.model = self._load_model()
        self.transform = T.Compose([T.ToTensor()])
        
        # COCO dataset classes
        self.class_names = [
            '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
            'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
            'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut',
            'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table', 'N/A', 'N/A',
            'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
            'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        self.elephant_class_id = 20  # COCO class ID for elephant
        logger.info("ElephantDetector initialized")

    def _load_model(self):
        """Load pre-trained Faster R-CNN model"""
        try:
            logger.info("Loading pre-trained Faster R-CNN model...")
            model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
            model.eval()
            logger.info("Model loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def detect(self, image_path):
        """Detect elephants in an image"""
        try:
            image = Image.open(image_path).convert("RGB")
            image_tensor = self.transform(image)
            
            with torch.no_grad():
                predictions = self.model([image_tensor])
            
            detections = []
            pred = predictions[0]
            
            for i in range(len(pred['labels'])):
                label = pred['labels'][i].item()
                score = pred['scores'][i].item()
                
                if label == self.elephant_class_id and score > self.confidence_threshold:
                    bbox = [int(coord) for coord in pred['boxes'][i].tolist()]
                    
                    detection = {
                        'species': 'elephant',
                        'confidence': score,
                        'bbox': bbox,
                        'class_id': label,
                        'class_name': self.class_names[label]
                    }
                    detections.append(detection)
            
            logger.info(f"Detected {len(detections)} elephants in {image_path}")
            return detections
            
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return []

    def detect_from_array(self, image_array):
        """Detect elephants from numpy array"""
        try:
            image = Image.fromarray(image_array)
            return self.detect_image(image)
        except Exception as e:
            logger.error(f"Error detecting from array: {e}")
            return []

# Global instance
detector = ElephantDetector()