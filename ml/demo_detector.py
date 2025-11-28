"""
Demo Script - Test the Wildlife Detector with Mock Data
Run this to test detections without needing real images or ML model
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.detector import WildlifeDetector, get_detector
import json


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_mock_detector():
    """Demonstrate mock detector functionality"""
    print_section("MOCK DETECTOR DEMO")
    
    print("Initializing mock detector...")
    detector = WildlifeDetector(use_mock=True)
    
    print("\nRunning 3 mock detections on a fake image...\n")
    
    for i in range(3):
        print(f"Detection Run {i+1}:")
        results = detector.detect(
            image_path="test_image_000.jpg",
            latitude=-1.5,
            longitude=35.3,
            conf_threshold=0.7
        )
        
        for result in results:
            print(f"  ✓ {result.species.capitalize()} - Confidence: {result.confidence:.2%}")
        
        if not results:
            print("  ℹ No detections (this happens randomly ~30% of the time)")
        print()


def demo_detector_switching():
    """Demonstrate mode switching"""
    print_section("DETECTOR MODE SWITCHING")
    
    detector = get_detector(use_mock=True)
    
    print(f"Current mode: {'MOCK' if detector.use_mock else 'REAL'}")
    print("\nSwitching to REAL mode...")
    
    try:
        detector.switch_mode(use_mock=False)
        print(f"✓ Mode switched to: {'MOCK' if detector.use_mock else 'REAL'}")
        print("✓ YOLOv8 model loaded successfully!")
    except ImportError:
        print("✗ YOLOv8 not installed. Install with: pip install ultralytics")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Switch back
    detector.switch_mode(use_mock=True)
    print(f"\nSwitched back to: {'MOCK' if detector.use_mock else 'REAL'}")


def demo_with_app_context():
    """Demonstrate with Flask app context (requires running app)"""
    print_section("DETECTION SERVICE DEMO (with Flask app)")
    
    try:
        from app import create_app
        from app.services.detection_services import get_detection_service
        
        print("Creating Flask app context...")
        app = create_app()
        
        with app.app_context():
            print("✓ App context created\n")
            
            # Get detection service
            service = get_detection_service(use_mock=True)
            
            # Get stats
            stats = service.get_stats()
            print("Detection Statistics:")
            print(f"  Total detections: {stats['total_detections']}")
            print(f"  Verified: {stats['verified']}")
            print(f"  False positives: {stats['false_positives']}")
            
            if stats['species']:
                print(f"  Species breakdown: {stats['species']}")
            else:
                print("  No species data yet")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure the Flask app is properly configured with database")


def print_info():
    """Print information about the detection system"""
    print_section("WILDLIFE DETECTOR SYSTEM - OVERVIEW")
    
    info = """
📚 ARCHITECTURE:

  ml/detector.py
    └─ WildlifeDetector class
       ├─ Mock Mode: Simulates detections for testing (no ML needed)
       └─ Real Mode: Uses YOLOv8 for actual object detection

  app/services/detection_services.py
    └─ DetectionService class
       └─ Integrates detector with Flask app
          ├─ Saves detections to database
          └─ Emits real-time updates via WebSocket

  app/routes/detections.py
    └─ REST API endpoints
       ├─ POST /api/detections - Upload image and run detection
       ├─ GET /api/detections - List all detections (paginated)
       ├─ GET /api/stats - Get detection statistics
       ├─ POST /api/mode - Switch between mock/real detection
       └─ GET /api/mode - Get current detection mode


🎯 MOCK MODE (Default for MVP):
  ✓ No dependencies needed
  ✓ Fast testing and development
  ✓ Simulates realistic detection patterns
  ✓ 70% chance of detection per image
  ✓ Random wildlife species and confidence scores

⚙️  REAL MODE (YOLOv8):
  ✓ Requires: pip install ultralytics
  ✓ Detects 80+ object classes including animals
  ✓ Filters results to wildlife only
  ✓ Requires GPU for reasonable performance
  ✓ Can use custom trained models


🚀 GETTING STARTED:

  1. Current setup: Uses MOCK mode by default
  
  2. To test with mock detections:
     POST /api/detections
     {
       "species": "elephant",
       "confidence": "0.95",
       "latitude": "-1.5",
       "longitude": "35.3"
     }
  
  3. To enable real YOLOv8:
     pip install ultralytics
     POST /api/mode { "use_mock": false }
  
  4. Check stats anytime:
     GET /api/stats


📝 WILDLIFE CLASSES SUPPORTED:
    elephant, lion, leopard, buffalo, giraffe, zebra,
    rhinoceros, hippopotamus, cheetah, hyena, wild dog,
    antelope, wildebeest, deer, bear, wolf
    """
    
    print(info)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Wildlife Detector Demo')
    parser.add_argument('--mode', choices=['mock', 'info', 'switch', 'app'], 
                       default='info',
                       help='Demo mode to run')
    
    args = parser.parse_args()
    
    if args.mode == 'mock':
        demo_mock_detector()
    elif args.mode == 'switch':
        demo_detector_switching()
    elif args.mode == 'app':
        demo_with_app_context()
    else:
        print_info()
        print("\n💡 Try running:")
        print("   python ml/demo_detector.py --mode mock")
        print("   python ml/demo_detector.py --mode switch")
        print("   python ml/demo_detector.py --mode app")
