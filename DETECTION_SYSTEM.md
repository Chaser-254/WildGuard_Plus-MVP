# Wildlife Detection System - WildGuard MVP

## Overview

This document explains the wildlife detection system integrated into WildGuard Plus MVP. It supports both **mock detection** (for MVP/testing) and **real YOLOv8** (for production).

## Architecture

```
WildGuard Detection System
├── ml/detector.py (Core ML module)
│   ├── WildlifeDetector class
│   ├── DetectionResult class
│   └── Mock & Real modes
│
├── app/services/detection_services.py (Business logic)
│   └── DetectionService class (integrates with Flask/DB)
│
├── app/routes/detections.py (REST API)
│   └── Detection endpoints
│
└── app/models/detection.py (Database)
    └── Detection model
```

## Detection Modes

### 1. Mock Mode (Default - MVP)

**Perfect for MVP because:**
- ✅ No dependencies or heavy libraries
- ✅ No GPU required
- ✅ Instant results for testing
- ✅ Realistic detection patterns
- ✅ Easy to test UI without real ML

**How it works:**
- 70% chance of detecting something per image
- Randomly selects 1-3 wildlife species
- Generates realistic confidence scores
- Returns location data

**Usage:**
```python
from ml.detector import WildlifeDetector

detector = WildlifeDetector(use_mock=True)  # Default
results = detector.detect(
    image_path="test.jpg",
    latitude=-1.5,
    longitude=35.3,
    conf_threshold=0.5
)

for result in results:
    print(f"{result.species}: {result.confidence:.2%}")
    # Output: elephant: 92.34%
```

### 2. Real Mode (YOLOv8)

**For production detection using pre-trained or custom models:**

**Setup:**
```bash
pip install ultralytics
```

**Usage:**
```python
detector = WildlifeDetector(use_mock=False)  # Load YOLOv8
# or with custom model:
detector = WildlifeDetector(use_mock=False, model_path="path/to/model.pt")
```

**Features:**
- Uses YOLOv8 (state-of-the-art object detection)
- Pre-trained on 80+ object classes (including animals)
- Automatically filters for wildlife only
- Supports custom trained models

**Supported Wildlife Classes:**
```
elephant, lion, leopard, buffalo, giraffe, zebra,
rhinoceros, hippopotamus, cheetah, hyena, wild dog,
antelope, wildebeest, deer, bear, wolf
```

## API Endpoints

### 1. Run Detection (POST)
```bash
POST /api/detections
Content-Type: multipart/form-data

image: <file>              # Optional: Image to detect
species: elephant          # Optional: Manual species entry
confidence: 0.95          # Optional: Manual confidence
latitude: -1.5            # Required for form submission
longitude: 35.3           # Required for form submission
conf_threshold: 0.5       # Optional: Min confidence threshold
```

**Response:**
```json
{
  "status": "success",
  "message": "Image processed. Found 2 detections.",
  "detections": [
    {
      "id": 1,
      "species": "elephant",
      "confidence": 0.92,
      "location": {"lat": -1.5, "lng": 35.3},
      "timestamp": "2025-11-26T16:14:15",
      "image_path": "uploads/test.jpg",
      "is_verified": false
    }
  ]
}
```

### 2. List Detections (GET)
```bash
GET /api/detections?page=1&per_page=10
```

**Response:**
```json
{
  "items": [...],
  "page": 1,
  "per_page": 10,
  "total": 42,
  "pages": 5
}
```

### 3. Get Detection Statistics (GET)
```bash
GET /api/stats
```

**Response:**
```json
{
  "total_detections": 42,
  "verified": 15,
  "false_positives": 2,
  "species": {
    "elephant": 18,
    "lion": 12,
    "leopard": 8,
    "buffalo": 4
  }
}
```

### 4. Get Current Mode (GET)
```bash
GET /api/mode
```

**Response:**
```json
{
  "use_mock": true,
  "mode": "MOCK (Simulated)"
}
```

### 5. Switch Detection Mode (POST)
```bash
POST /api/mode
Content-Type: application/json

{"use_mock": false}
```

**Response:**
```json
{
  "status": "success",
  "message": "Detection mode switched to REAL (YOLOv8)",
  "use_mock": false
}
```

## Integration with Flask

### 1. Initialize in your app:
```python
from app.services.detection_services import get_detection_service

# In your route or service:
detection_service = get_detection_service(use_mock=True)
detections, success = detection_service.process_image(
    image_path="path/to/image.jpg",
    latitude=-1.5,
    longitude=35.3,
    socketio=socketio  # For real-time updates
)
```

### 2. Database Integration:
Detections are automatically saved to the `Detection` database table with:
- `id` (auto-incrementing)
- `species` (detected wildlife type)
- `confidence` (detection confidence 0-1)
- `latitude`, `longitude` (location)
- `timestamp` (when detected)
- `image_path` (path to uploaded image)
- `is_verified` (ranger verification status)
- `is_false_positive` (false alarm flag)

### 3. Real-time Updates:
When a detection is made, it's automatically emitted via WebSocket:
```javascript
// In frontend (detections.html)
socket.on('new_detection', (detection) => {
  console.log('New detection:', detection);
  // Update UI in real-time
});
```

## Testing

### Run Demo Script:
```bash
# Show info about detection system
python ml/demo_detector.py

# Test mock detector
python ml/demo_detector.py --mode mock

# Test mode switching
python ml/demo_detector.py --mode switch

# Test with Flask app (requires app running)
python ml/demo_detector.py --mode app
```

### Manual Testing via API:
```bash
# Start Flask app
python run.py

# Test with mock mode (default)
curl -X POST http://localhost:5000/api/detections \
  -F "image=@test.jpg" \
  -F "latitude=-1.5" \
  -F "longitude=35.3"

# Check current mode
curl http://localhost:5000/api/mode

# Switch to real mode (if YOLOv8 installed)
curl -X POST http://localhost:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"use_mock": false}'

# Get stats
curl http://localhost:5000/api/stats
```

## Roadmap: Mock → Real

### MVP (Current):
- ✅ Mock detector fully functional
- ✅ Mock data looks realistic
- ✅ Easy to test UI/UX
- ✅ Ready for demo

### Phase 1 (Next):
- Deploy pre-trained YOLOv8
- Add GPU support (AWS, GCP, etc.)
- Test with real animal images

### Phase 2 (Future):
- Fine-tune YOLOv8 on elephant images
- Improve confidence scores
- Add multi-animal tracking
- Deploy to edge devices

## Troubleshooting

### YOLOv8 Not Found
```bash
pip install ultralytics
# or
pip install -r requirements.txt  # Updates requirements.txt with ultralytics
```

### Mode Switching Fails
- Check logs: `current_app.logger`
- Make sure both modes are properly initialized

### Detections Not Saving
- Check database connection
- Verify `Detection` model exists and is migrated
- Check `app/static/uploads` folder has write permissions

### Performance Issues
- Mock mode: Very fast (should be instant)
- Real mode: Depends on GPU availability
  - CPU: ~2-5s per image (not recommended)
  - GPU: ~0.2-0.5s per image (recommended)

## Configuration

### Environment Variables (Optional):
```bash
# Detection confidence threshold (default: 0.5)
DETECTION_CONF_THRESHOLD=0.6

# Number of detections per page
DETECTIONS_PER_PAGE=20

# Custom YOLOv8 model path
CUSTOM_MODEL_PATH=/path/to/model.pt
```

### File Structure:
```
app/
├── models/
│   └── detection.py      # Detection database model
├── routes/
│   └── detections.py     # API endpoints
└── services/
    └── detection_services.py  # Business logic

ml/
├── detector.py           # Core ML module
└── demo_detector.py      # Demo/test script

static/
└── uploads/              # Uploaded images directory
```

## Next Steps

1. **Test the mock detector:**
   ```bash
   python ml/demo_detector.py --mode mock
   ```

2. **Upload an image via the UI:**
   - Go to http://localhost:5000/detections
   - Fill in the form and submit
   - See mock detections appear

3. **Enable real detection (optional):**
   ```bash
   pip install ultralytics
   # Then switch mode via API or code
   ```

4. **Train custom model (future):**
   - Collect elephant images
   - Fine-tune YOLOv8 on your dataset
   - Deploy custom model

## Support

For questions or issues:
1. Check logs: `app.logger.info()`
2. Run demo script for diagnostics
3. Review this documentation
4. Check API responses for error messages

---

**Status:** ✅ MVP Ready
**Detection Mode:** Mock (Simulated)
**Real ML:** Ready to enable (requires YOLOv8)
