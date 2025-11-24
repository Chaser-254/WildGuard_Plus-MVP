import cv2
import numpy as np
from PIL import Image
import io

def resize_image(image, max_size=800):
    """Resize image while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    if max(height, width) <= max_size:
        return image
    
    if height > width:
        new_height = max_size
        new_width = int(width * (max_size / height))
    else:
        new_width = max_size
        new_height = int(height * (max_size / width))
    
    return cv2.resize(image, (new_width, new_height))

def draw_detections(image, detections):
    """Draw bounding boxes and labels on image"""
    image_with_boxes = image.copy()
    
    for detection in detections:
        bbox = detection['bbox']
        confidence = detection['confidence']
        species = detection['species']
        
        # Draw bounding box
        cv2.rectangle(image_with_boxes, 
                     (int(bbox[0]), int(bbox[1])), 
                     (int(bbox[2]), int(bbox[3])), 
                     (0, 255, 0), 2)
        
        # Draw label background
        label = f"{species} {confidence:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        
        cv2.rectangle(image_with_boxes,
                     (int(bbox[0]), int(bbox[1]) - label_size[1] - 10),
                     (int(bbox[0]) + label_size[0], int(bbox[1])),
                     (0, 255, 0), -1)
        
        # Draw label text
        cv2.putText(image_with_boxes, label,
                   (int(bbox[0]), int(bbox[1]) - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    return image_with_boxes

def image_to_bytes(image):
    """Convert PIL Image to bytes"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()