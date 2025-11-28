"""
Stream Service - manage camera streams and run periodic detection on frames
"""
import threading
import time
import os
import logging
from typing import Dict, Optional
from app.services.detection_services import get_detection_service

logger = logging.getLogger(__name__)


class StreamWorker:
    def __init__(self, stream_id: str, url: str, interval: float = 5.0, use_mock: bool = True):
        self.stream_id = stream_id
        self.url = url
        self.interval = interval
        self.use_mock = use_mock
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.capture = None

    def start(self):
        logger.info(f"Starting stream worker {self.stream_id} for {self.url}")
        self._thread.start()

    def stop(self):
        logger.info(f"Stopping stream worker {self.stream_id}")
        self._stop_event.set()
        try:
            if self.capture:
                try:
                    self.capture.release()
                except Exception:
                    pass
        except Exception:
            pass

    def _run(self):
        # Use OpenCV to open the stream. If it's a file, it works too.
        try:
            # Import cv2 lazily so tests / environments without OpenCV can still import module
            try:
                import cv2
            except Exception:
                logger.warning("OpenCV (cv2) not available; stream worker will not run frames")
                return

            self.capture = cv2.VideoCapture(self.url)
            if not self.capture.isOpened():
                logger.error(f"Unable to open stream: {self.url}")
                return

            detection_service = get_detection_service(use_mock=self.use_mock)

            while not self._stop_event.is_set():
                # Read a frame
                ret, frame = self.capture.read()
                if not ret:
                    logger.warning(f"Stream {self.stream_id}: failed to read frame")
                    # Wait and try again
                    time.sleep(1.0)
                    continue

                # Save frame temporarily to a file and run detection
                tmp_dir = os.path.join(os.getcwd(), 'tmp_stream_frames')
                os.makedirs(tmp_dir, exist_ok=True)
                timestamp = int(time.time() * 1000)
                tmp_path = os.path.join(tmp_dir, f"{self.stream_id}_{timestamp}.jpg")
                try:
                    cv2.imwrite(tmp_path, frame)
                except Exception:
                    logger.exception(f"Failed to write frame to {tmp_path}")
                    continue

                try:
                    # Import socketio lazily to avoid circular imports during app startup
                    try:
                        from app import socketio as app_socketio
                    except Exception:
                        app_socketio = None

                    detection_service.process_image(
                        image_path=tmp_path,
                        latitude=None,
                        longitude=None,
                        conf_threshold=0.5,
                        socketio=app_socketio,
                        camera_id=self.stream_id
                    )
                except Exception as e:
                    logger.exception(f"Error processing frame from stream {self.stream_id}: {e}")

                # Remove the temporary frame to save disk
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

                # Sleep for interval seconds before next frame
                time.sleep(self.interval)

        except Exception as e:
            logger.exception(f"Stream worker {self.stream_id} crashed: {e}")
        finally:
            try:
                if self.capture:
                    self.capture.release()
            except Exception:
                pass


class StreamManager:
    def __init__(self):
        self.workers: Dict[str, StreamWorker] = {}
        self.lock = threading.Lock()

    def add_stream(self, stream_id: str, url: str, interval: float = 5.0, use_mock: bool = True) -> bool:
        with self.lock:
            if stream_id in self.workers:
                logger.warning(f"Stream {stream_id} already registered")
                return False
            worker = StreamWorker(stream_id, url, interval=interval, use_mock=use_mock)
            self.workers[stream_id] = worker
            worker.start()
            return True

    def remove_stream(self, stream_id: str) -> bool:
        with self.lock:
            worker = self.workers.get(stream_id)
            if not worker:
                logger.warning(f"Stream {stream_id} not found")
                return False
            worker.stop()
            del self.workers[stream_id]
            return True

    def list_streams(self):
        with self.lock:
            return [{
                'id': sid,
                'url': w.url,
                'interval': w.interval,
                'running': not w._stop_event.is_set()
            } for sid, w in self.workers.items()]


# Global manager instance
_stream_manager: Optional[StreamManager] = None


def get_stream_manager() -> StreamManager:
    global _stream_manager
    if _stream_manager is None:
        _stream_manager = StreamManager()
    return _stream_manager
