import requests
import json
import random
import time
import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000/api"

def simulate_detection():
    """Simulate an elephant detection event"""
    cameras = [
        {'id': 'cam_001', 'lat': -1.9441, 'lng': 30.0619, 'name': 'Mtajua C'},
        {'id': 'cam_002', 'lat': -1.9500, 'lng': 30.0700, 'name': 'Mtakuja, Near St. Nobert Tangini'},
        {'id': 'cam_003', 'lat': -1.9300, 'lng': 30.0500, 'name': 'Njoro A Village, along the springs'}
    ]
    
    camera = random.choice(cameras)
    
    # Add some random variation to make it realistic
    lat_variation = (random.random() - 0.5) * 0.01
    lng_variation = (random.random() - 0.5) * 0.01
    
    detection_data = {
        'species': 'elephant',
        'confidence': round(0.7 + random.random() * 0.3, 2),
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
            f"{BASE_URL}/alert",
            json=detection_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        result = response.json()
        
        if result.get('status') == 'success':
            print(f"Detection from {camera['name']} - Confidence: {detection_data['confidence']:.1%}")
            return True
        elif result.get('status') == 'cooldown':
            print(f"Cooldown: Recent detection from {camera['name']}")
            return True
        else:
            print(f"Failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def demo_herd_movement():
    """Simulate a herd of elephants moving between locations"""
    print("Simulating herd movement...")
    
    # camera locations
    movements = [
        ('cam_001', 'Main Waterhole'),
        ('cam_002', 'Northern Corridor'), 
        ('cam_003', 'Southern Border'),
        ('cam_001', 'Main Waterhole'),
    ]
    
    for camera_id, camera_name in movements:
        print(f"Herd moving to {camera_name}...")
        time.sleep(8)
        
        herd_size = random.randint(2, 4)
        for i in range(herd_size):
            time.sleep(2)
            
            detection_data = {
                'species': 'elephant',
                'confidence': round(0.8 + random.random() * 0.2, 2),
                'camera_id': camera_id,
                'location': {
                    'lat': -1.9441 + (random.random() - 0.5) * 0.01,
                    'lng': 30.0619 + (random.random() - 0.5) * 0.01
                },
                'image_path': f'/static/images/detection_{random.randint(1, 3)}.jpg'
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/alert",
                    json=detection_data,
                    headers={'Content-Type': 'application/json'}
                )
                print(f"Elephant {i+1} detected at {camera_name}")
            except:
                print(f"Failed to detect elephant {i+1}")

def main():
    print("WildGuardPlus Detection System")
    print("=" * 50)
    print("Flask server is running on http://localhost:5000")
    print()
    
    while True:
        print("Dtection Options:")
        print("1. Single random detection")
        print("2. Continuous simulation (for background during presentation)")
        print("3. Herd movement simulation")
        print("4. Exit")
        print()
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == '1':
            simulate_detection()
        elif choice == '2':
            print("🔄 Starting continuous simulation...")
            print("Press Ctrl+C to stop")
            print()
            try:
                while True:
                    interval = random.randint(15, 45)
                    time.sleep(interval)
                    simulate_detection()
            except KeyboardInterrupt:
                print("\n Simulation stopped")
        elif choice == '3':
            demo_herd_movement()
        elif choice == '4':
            print("Thank you for using WildGuard Plus!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print()

if __name__ == '__main__':
    main()