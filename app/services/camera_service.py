"""
Camera Service - Manages camera streams and background workers
"""

import threading
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CameraSource:
    """Represents a single camera source"""
    
    def __init__(self, camera_id: str, source: str, latitude: float, longitude: float,
                 name: str = None):
        """
        Initialize a camera source.
        
        Args:
            camera_id: Unique identifier (e.g., 'cam-001')
            source: Camera source (0 for webcam, RTSP URL, file path, etc.)
            latitude: GPS latitude of camera location
            longitude: GPS longitude of camera location
            name: Human-readable name
        """
        self.camera_id = camera_id
        self.source = source
        self.latitude = latitude
        self.longitude = longitude
        self.name = name or camera_id
        self.is_active = True
        self.last_frame_time = None
        self.frame_count = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API/DB"""
        return {
            'camera_id': self.camera_id,
            'name': self.name,
            'source': self.source,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_active': self.is_active,
            'last_frame_time': self.last_frame_time.isoformat() if self.last_frame_time else None,
            'frame_count': self.frame_count
        }


class StreamWorker(threading.Thread):
    """Background worker for processing camera streams"""
    
    def __init__(self, camera: CameraSource, detector, classifier,
                 detection_callback=None, interval: float = 2.0):
        """
        Initialize stream worker.
        
        Args:
            camera: CameraSource instance
            detector: WildlifeDetector instance
            classifier: SpeciesClassifier instance
            detection_callback: Callable to invoke when detection found
            interval: Seconds between frame processing
        """
        super().__init__(daemon=True)
        self.camera = camera
        self.detector = detector
        self.classifier = classifier
        self.detection_callback = detection_callback
        self.interval = interval
        self.running = False
        self._lock = threading.Lock()
    
    def run(self):
        """Main stream processing loop"""
        try:
            import cv2
        except ImportError:
            logger.warning("OpenCV not installed. Stream workers disabled.")
            return
        
        self.running = True
        logger.info(f"Starting stream worker for {self.camera.camera_id}")
        
        cap = None
        try:
            # Try to open camera source
            cap = cv2.VideoCapture(self.camera.source)
            if not cap.isOpened():
                logger.error(f"Failed to open camera source: {self.camera.source}")
                self.camera.is_active = False
                return
            
            logger.info(f"Camera {self.camera.camera_id} opened successfully")
            self.camera.is_active = True
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame from {self.camera.camera_id}")
                    break
                
                with self._lock:
                    self.camera.last_frame_time = datetime.utcnow()
                    self.camera.frame_count += 1
                
                # Process frame every `interval` seconds
                time.sleep(self.interval)
        
        except Exception as e:
            logger.error(f"Error in stream worker for {self.camera.camera_id}: {e}")
        
        finally:
            if cap:
                cap.release()
            self.camera.is_active = False
            self.running = False
            logger.info(f"Stream worker stopped for {self.camera.camera_id}")
    
    def stop(self):
        """Stop the stream worker"""
        self.running = False


class CameraManager:
    """Manages multiple camera streams"""
    
    def __init__(self, detector=None, classifier=None):
        """
        Initialize camera manager.
        
        Args:
            detector: WildlifeDetector instance
            classifier: SpeciesClassifier instance
        """
        self.cameras: Dict[str, CameraSource] = {}
        self.workers: Dict[str, StreamWorker] = {}
        self.detector = detector
        self.classifier = classifier
        self._lock = threading.Lock()
    
    def add_camera(self, camera_id: str, source: str, latitude: float,
                   longitude: float, name: str = None) -> CameraSource:
        """Add a new camera source"""
        with self._lock:
            if camera_id in self.cameras:
                logger.warning(f"Camera {camera_id} already exists")
                return self.cameras[camera_id]
            
            camera = CameraSource(camera_id, source, latitude, longitude, name)
            self.cameras[camera_id] = camera
            logger.info(f"Added camera {camera_id}")
            return camera
    
    def remove_camera(self, camera_id: str) -> bool:
        """Remove a camera and stop its worker"""
        with self._lock:
            if camera_id not in self.cameras:
                return False
            
            # Stop worker if running
            if camera_id in self.workers:
                self.workers[camera_id].stop()
                self.workers[camera_id].join(timeout=5)
                del self.workers[camera_id]
            
            del self.cameras[camera_id]
            logger.info(f"Removed camera {camera_id}")
            return True
    
    def start_stream(self, camera_id: str, detection_callback=None,
                    interval: float = 2.0) -> bool:
        """Start streaming from a camera"""
        with self._lock:
            if camera_id not in self.cameras:
                logger.error(f"Camera {camera_id} not found")
                return False
            
            if camera_id in self.workers and self.workers[camera_id].running:
                logger.warning(f"Camera {camera_id} already streaming")
                return False
            
            camera = self.cameras[camera_id]
            worker = StreamWorker(
                camera, self.detector, self.classifier,
                detection_callback=detection_callback,
                interval=interval
            )
            worker.start()
            self.workers[camera_id] = worker
            logger.info(f"Started streaming from {camera_id}")
            return True
    
    def stop_stream(self, camera_id: str) -> bool:
        """Stop streaming from a camera"""
        with self._lock:
            if camera_id not in self.workers:
                return False
            
            worker = self.workers[camera_id]
            worker.stop()
            worker.join(timeout=5)
            del self.workers[camera_id]
            logger.info(f"Stopped streaming from {camera_id}")
            return True
    
    def get_camera(self, camera_id: str) -> Optional[CameraSource]:
        """Get camera info"""
        return self.cameras.get(camera_id)
    
    def list_cameras(self) -> List[Dict]:
        """List all cameras as dicts"""
        return [cam.to_dict() for cam in self.cameras.values()]
    
    def get_active_cameras(self) -> List[CameraSource]:
        """Get all active cameras"""
        return [cam for cam in self.cameras.values() if cam.is_active]
