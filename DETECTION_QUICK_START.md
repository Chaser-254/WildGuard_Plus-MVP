# Wildlife Detection System - Quick Start Guide

## What You Have

A complete wildlife detection system for WildGuard MVP with:

✅ **Mock Detector** - Ready to use NOW (simulates detections)  
✅ **Real YOLOv8** - Optional (for actual object detection)  
✅ **Flask Integration** - Fully integrated with your app  
✅ **REST API** - Easy to use endpoints  
✅ **Real-time Updates** - WebSocket support  

## Current Status: MVP with Mock Detection

Your system is ready to use with **mock detection** (simulated detections for testing).

## Getting Started (5 minutes)

### 1. Start Your Flask App
```bash
python run.py
```
Opens on http://127.0.0.1:5000

### 2. Test the Detection UI
- Click **"Detection engine"** in sidebar
- Upload an image (or manually enter species/confidence)
- Click **"Submit Detection"**
- See simulated detections appear!

### 3. Check the API
```bash
# Get all detections
curl http://localhost:5000/api/detections

# Get statistics
curl http://localhost:5000/api/stats

# Check detection mode
curl http://localhost:5000/api/mode
```

## How It Works Right Now

```
User uploads image
        ↓
Flask receives request
        ↓
Mock Detector runs (simulates detection)
        ↓
Returns realistic data (species + confidence)
        ↓
Saved to database
        ↓
Shown in UI + WebSocket update
```

**Result:** You get a working MVP that looks like real detection! 🎉

## Test with Demo Script

```bash
# See system info and supported wildlife
python ml/demo_detector.py

# Test mock detector (generates fake detections)
python ml/demo_detector.py --mode mock

# Show how mode switching works
python ml/demo_detector.py --mode switch
```

## Enable Real YOLOv8 Detection (Optional)

When you're ready to use actual object detection:

### Step 1: Install YOLOv8
```bash
pip install ultralytics
```

### Step 2: Switch Mode via API
```bash
curl -X POST http://localhost:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"use_mock": false}'
```

### Step 3: Upload Image with Real Detections
- Go to http://localhost:5000/detections
- Upload an image with animals
- Now it runs REAL YOLOv8 instead of mock!

## File Structure

```
ml/
├── detector.py          ← Core detection logic
├── demo_detector.py     ← Test script
└── models/
    └── download_models.py  ← YOLOv8 setup

app/
├── routes/
│   └── detections.py    ← API endpoints
├── services/
│   └── detection_services.py  ← Business logic
└── models/
    └── detection.py     ← Database model

DETECTION_SYSTEM.md  ← Full documentation
```

## API Reference

### Upload Image & Detect
```bash
POST /api/detections
Content-Type: multipart/form-data

image: <file>
latitude: -1.5
longitude: 35.3
conf_threshold: 0.5
```

### Get All Detections
```bash
GET /api/detections?page=1&per_page=10
```

### Get Statistics
```bash
GET /api/stats
```

### Check Detection Mode
```bash
GET /api/mode
```

### Switch Mode
```bash
POST /api/mode
{"use_mock": true/false}
```

## Supported Animals (Real Mode)

When using YOLOv8, these are detected:
```
elephant, lion, leopard, buffalo, giraffe, zebra,
rhinoceros, hippopotamus, cheetah, hyena, wild dog,
antelope, wildebeest, deer, bear, wolf
```

## Performance

| Mode | Speed | Quality | Needs GPU |
|------|-------|---------|-----------|
| Mock | Instant | Test data | ❌ |
| YOLOv8 (CPU) | 2-5s/image | Real | ❌ |
| YOLOv8 (GPU) | 0.2-0.5s/image | Real | ✅ |

## Common Issues & Solutions

### "Image not found" error
- Make sure image path is correct
- Check `app/static/uploads/` folder exists

### "ultralytics not installed"
```bash
pip install ultralytics
```

### Detections not appearing
- Check database connection
- Run: `curl http://localhost:5000/api/stats`
- Check Flask console for errors

### Mode switch not working
- Make sure YOLOv8 is installed for real mode
- Check API response: `curl http://localhost:5000/api/mode`

## Next Steps

### For Demo/MVP:
✅ Keep using mock mode (it works great for demos!)

### To Test Real Detection:
1. `pip install ultralytics`
2. Collect some animal images
3. Switch to real mode
4. Test with your images

### To Train Custom Model:
1. Collect ~500-1000 elephant images
2. Use YOLOv8 fine-tuning
3. Deploy custom model

## Code Examples

### Python (Backend)
```python
from app.services.detection_services import get_detection_service

service = get_detection_service(use_mock=True)
detections, success = service.process_image(
    image_path="path/to/image.jpg",
    latitude=-1.5,
    longitude=35.3
)

print(f"Found {len(detections)} detections")
for d in detections:
    print(f"  - {d.species}: {d.confidence:.2%}")
```

### JavaScript (Frontend)
```javascript
// Already implemented in app/templates/pages/detections.html

// Upload and detect
fetch('/api/detections', {
  method: 'POST',
  body: formData  // includes image + location
})
.then(r => r.json())
.then(data => {
  console.log('Detections:', data.detections);
  // Update UI with results
});

// Listen for real-time updates
socket.on('new_detection', (detection) => {
  console.log('Real-time detection:', detection);
});
```

## Frequently Asked Questions

**Q: Can I use mock mode for production?**  
A: No, mock is for MVP/testing only. Use real YOLOv8 for production.

**Q: Will mock mode affect my data?**  
A: No, both modes save the same way. Detections are identical in database.

**Q: How do I switch back from real to mock?**  
A: `curl -X POST http://localhost:5000/api/mode -H "Content-Type: application/json" -d '{"use_mock": true}'`

**Q: Can I use a custom trained model?**  
A: Yes! Initialize with: `WildlifeDetector(use_mock=False, model_path="path/to/model.pt")`

**Q: Why mock mode?**  
A: MVP development is fast without heavy ML dependencies. Perfect for demos and testing UI/UX.

## Full Documentation

See **DETECTION_SYSTEM.md** for comprehensive documentation.

---

🎉 **You're all set!** Start testing detections now:
```bash
python run.py
# Visit: http://localhost:5000/detections
```
