"""
Quick test to verify the detection system is working
Run this to ensure everything is properly integrated
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from ml.detector import WildlifeDetector, get_detector
        print("  ✓ ml.detector imported")
        
        from app.services.detection_services import get_detection_service
        print("  ✓ app.services.detection_services imported")
        
        from app.models import Detection
        print("  ✓ app.models.Detection imported")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False


def test_mock_detector():
    """Test mock detector"""
    print("\nTesting mock detector...")
    try:
        from ml.detector import WildlifeDetector
        
        detector = WildlifeDetector(use_mock=True)
        print("  ✓ Mock detector initialized")
        
        results = detector.detect(
            image_path="test.jpg",
            latitude=-1.5,
            longitude=35.3
        )
        print(f"  ✓ Detection ran successfully")
        print(f"    Results: {len(results)} objects detected")
        
        if results:
            for r in results:
                print(f"    - {r.species}: {r.confidence:.2%}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_with_app():
    """Test with Flask app context"""
    print("\nTesting with Flask app...")
    try:
        from app import create_app
        from app.services.detection_services import get_detection_service
        
        app = create_app()
        print("  ✓ Flask app created")
        
        with app.app_context():
            print("  ✓ App context active")
            
            service = get_detection_service(use_mock=True)
            print("  ✓ Detection service created")
            
            stats = service.get_stats()
            print("  ✓ Got statistics")
            print(f"    Total detections: {stats['total_detections']}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detector_switching():
    """Test mode switching"""
    print("\nTesting mode switching...")
    try:
        from ml.detector import get_detector
        
        detector = get_detector(use_mock=True)
        print(f"  ✓ Initial mode: {'MOCK' if detector.use_mock else 'REAL'}")
        
        detector.switch_mode(use_mock=False)
        print(f"  ✓ Switched to: {'MOCK' if detector.use_mock else 'REAL'}")
        
        detector.switch_mode(use_mock=True)
        print(f"  ✓ Switched back to: {'MOCK' if detector.use_mock else 'REAL'}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("  WILDGUARD DETECTION SYSTEM - INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Mock Detector", test_mock_detector()))
    results.append(("Mode Switching", test_detector_switching()))
    results.append(("Flask Integration", test_with_app()))
    
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Detection system is ready to use.")
        print("\nNext steps:")
        print("  1. Start Flask: python run.py")
        print("  2. Visit: http://localhost:5000/detections")
        print("  3. Test detection upload")
        print("\nOr run the demo: python ml/demo_detector.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See above for details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
