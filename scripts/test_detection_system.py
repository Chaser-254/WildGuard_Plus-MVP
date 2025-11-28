#!/usr/bin/env python
"""
Quick Test Checklist for WildGuard Detection System

This script verifies all components are working correctly.
"""

import sys
import requests
import json

BASE_URL = 'http://localhost:5000'


def test_server_running():
    """Check if Flask server is running"""
    print("1️⃣ Testing server connectivity...")
    try:
        r = requests.get(f'{BASE_URL}/api/system/health', timeout=5)
        if r.status_code == 200:
            print("   ✅ Server is running")
            return True
        else:
            print(f"   ❌ Server returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot reach server: {e}")
        print(f"   💡 Make sure Flask is running: python run.py")
        return False


def test_system_status():
    """Check system status"""
    print("\n2️⃣ Checking system status...")
    try:
        r = requests.get(f'{BASE_URL}/api/system/status', timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            system = data.get('system', {})
            print(f"   ✅ Detection Mode: {system.get('detection_mode')}")
            print(f"   ✅ Cameras: {system.get('cameras_count')}")
            print(f"   ✅ Species Supported: {len(system.get('available_species', []))}")
            return True
        else:
            print(f"   ❌ {data.get('message')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_detection_mode():
    """Check current detection mode"""
    print("\n3️⃣ Checking detection mode...")
    try:
        r = requests.get(f'{BASE_URL}/api/system/detection-mode', timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            mode = data.get('mode')
            print(f"   ✅ Current Mode: {mode.upper()}")
            return True
        else:
            print(f"   ❌ {data.get('message')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_model_info():
    """Get model information"""
    print("\n4️⃣ Checking model information...")
    try:
        r = requests.get(f'{BASE_URL}/api/system/model-info', timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            model = data.get('model', {})
            print(f"   ✅ Model: {model.get('name')}")
            print(f"   ✅ Device: {model.get('device', 'N/A')}")
            if model.get('gpu_device'):
                print(f"   ✅ GPU: {model.get('gpu_device')}")
            return True
        else:
            print(f"   ❌ {data.get('message')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_species_list():
    """Get supported species"""
    print("\n5️⃣ Checking supported species...")
    try:
        r = requests.get(f'{BASE_URL}/api/system/species-list', timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            total = data.get('total_species', 0)
            print(f"   ✅ Total Species: {total}")
            species = data.get('species', [])
            if species:
                print(f"   Examples: {', '.join([s['name'] for s in species[:5]])}")
            return True
        else:
            print(f"   ❌ {data.get('message')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_detections():
    """Test getting detections"""
    print("\n6️⃣ Checking detections API...")
    try:
        r = requests.get(f'{BASE_URL}/api/detections/recent', timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            count = data.get('count', 0)
            print(f"   ✅ Total Detections: {count}")
            return True
        else:
            print(f"   ❌ {data.get('message')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_dashboard_summary():
    """Test dashboard summary"""
    print("\n7️⃣ Checking dashboard summary...")
    try:
        r = requests.get(f'{BASE_URL}/api/detections/dashboard-summary', timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            summary = data.get('summary', {})
            print(f"   ✅ Total Detections: {summary.get('total_detections', 0)}")
            print(f"   ✅ Verified: {summary.get('verified_detections', 0)}")
            print(f"   ✅ High Confidence: {summary.get('high_confidence_count', 0)}")
            print(f"   ✅ Active Cameras: {summary.get('active_cameras', 0)}")
            return True
        else:
            print(f"   ❌ {data.get('message')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_database():
    """Test database connectivity"""
    print("\n8️⃣ Checking database...")
    try:
        # Try to get detections to verify DB is accessible
        r = requests.get(f'{BASE_URL}/api/detections/recent?limit=1', timeout=5)
        if r.status_code == 200:
            print("   ✅ Database is accessible")
            return True
        else:
            print(f"   ❌ Database error (status {r.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("🦁 WildGuard Detection System - Test Checklist")
    print("="*60)
    
    tests = [
        test_server_running,
        test_system_status,
        test_detection_mode,
        test_model_info,
        test_species_list,
        test_detections,
        test_dashboard_summary,
        test_database,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All systems operational!")
        print("\n📌 Next Steps:")
        print("   1. Visit: http://localhost:5000/test-detection")
        print("   2. Click 'Simulate Detection' button")
        print("   3. Check dashboard updates")
        print("   4. Try uploading real images")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("\n💡 Troubleshooting:")
        print("   - Ensure Flask server is running: python run.py")
        print("   - Check database is created: ls instance/")
        print("   - Verify no port conflicts: netstat -an | find \"5000\"")
        return 1


if __name__ == '__main__':
    sys.exit(main())
