"""
Detection Mode Configuration

Set the detection mode for the application:
- DETECTION_MODE = 'mock'   : Use mock detector (no ML model needed)
- DETECTION_MODE = 'yolov8' : Use real YOLOv8 detector (requires ultralytics)

Detection Confidence Thresholds:
- ALERT_THRESHOLD: Minimum confidence to send alerts (default: 0.8 = 80%)
- DETECTION_THRESHOLD: Minimum confidence to save detection (default: 0.5 = 50%)
"""

import os

# Detection mode
DETECTION_MODE = os.environ.get('DETECTION_MODE', 'mock')  # 'mock' or 'yolov8'

# Use GPU if available (for YOLOv8)
USE_GPU = os.environ.get('USE_GPU', 'true').lower() in ('true', '1', 'yes')

# Confidence thresholds
ALERT_THRESHOLD = float(os.environ.get('ALERT_THRESHOLD', 0.8))      # 80%
DETECTION_THRESHOLD = float(os.environ.get('DETECTION_THRESHOLD', 0.5))  # 50%

# Model configuration
YOLOV8_MODEL = os.environ.get('YOLOV8_MODEL', 'yolov8m.pt')  # nano, small, medium, large, xlarge
CUSTOM_MODEL_PATH = os.environ.get('CUSTOM_MODEL_PATH', None)

# Processing settings
MAX_DETECTIONS_PER_IMAGE = int(os.environ.get('MAX_DETECTIONS_PER_IMAGE', 100))
IMAGE_SIZE = int(os.environ.get('IMAGE_SIZE', 640))  # YOLOv8 inference size

# Camera settings
CAMERA_FRAME_INTERVAL = float(os.environ.get('CAMERA_FRAME_INTERVAL', 2.0))  # seconds
CAMERA_TIMEOUT = int(os.environ.get('CAMERA_TIMEOUT', 30))  # seconds

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
