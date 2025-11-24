import requests
import json
import random
import time
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraSimulator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.cameras = [
            {'id': 'cam_001', 'lat': -1.9441, 'lng': 30.0619, 'name': 'Main Waterhole'},
            {'id': 'cam_002', 'lat': -1.9500, 'lng': 30.0700, 'name': 'Northern Corridor'},
            {'id': 'cam_003', 'lat': -1.9300, 'lng': 30.0500, 'name': 'Southern Border'}
        ]
        self.is_running = False
        
    def simulate_detection(self, camera_id=None):
        """Simulate an elephant detection from a camera"""
        if not camera_id:
            camera = random.choice(self.cameras)
        else:
            camera = next((cam for cam in self.cameras if cam['id'] == camera_id), self.cameras[0])
        
        # Add some random variation to location
        lat_variation = (random.random() - 0.5) * 0.02  # ~2km variation
        lng_variation = (random.random() - 0.5) * 0.02
        
        detection_data = {
            'species': 'elephant',
            'confidence': round(0.7 + random.random() * 0.3, 2),  # 0.7-1.0
            'camera_id': camera['id'],
            'location': {
                'lat': camera['lat'] + lat_variation,
                'lng': camera['lng'] + lng_variation
            },
            'image_path': f'/static/images/detection_{random.randint(1, 3)}.jpg',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/alert",
                json=detection_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Detection simulated from {camera['id']} - Confidence: {detection_data['confidence']}")
                return True
            else:
                logger.warning(f"⚠️ Detection simulation failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending detection: {e}")
            return False
    
    def start_continuous_simulation(self, interval_range=(10, 30)):
        """Start continuous simulation with random intervals"""
        self.is_running = True
        logger.info(f"🚀 Starting continuous simulation with intervals {interval_range} seconds")
        
        try:
            while self.is_running:
                # Random interval between detections
                interval = random.randint(interval_range[0], interval_range[1])
                time.sleep(interval)
                
                # 80% chance to simulate a detection
                if random.random() > 0.2:
                    self.simulate_detection()
                    
        except KeyboardInterrupt:
            self.stop_simulation()
    
    def stop_simulation(self):
        """Stop the continuous simulation"""
        self.is_running = False
        logger.info("🛑 Simulation stopped")
    
    def simulate_herd_movement(self, herd_size=3, movement_steps=5):
        """Simulate a herd of elephants moving between cameras"""
        logger.info(f"🐘 Simulating herd movement with {herd_size} elephants")
        
        for step in range(movement_steps):
            logger.info(f"🏃‍♂️ Herd movement step {step + 1}/{movement_steps}")
            
            for i in range(herd_size):
                time.sleep(random.randint(2, 5))  # Stagger detections
                self.simulate_detection()
            
            if step < movement_steps - 1:
                time.sleep(10)  # Wait before next movement

def main():
    simulator = CameraSimulator()
    
    print("ElephantAI Camera Simulator")
    print("=" * 40)
    print("1. Single detection")
    print("2. Continuous simulation")
    print("3. Herd movement simulation")
    print("4. Exit")
    
    while True:
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            simulator.simulate_detection()
        elif choice == '2':
            try:
                simulator.start_continuous_simulation()
            except KeyboardInterrupt:
                print("\nSimulation stopped by user")
        elif choice == '3':
            simulator.simulate_herd_movement()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()