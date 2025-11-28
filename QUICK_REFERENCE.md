# 🦁 WildGuard Quick Reference Card

## ⚡ Start in 30 seconds

```bash
# Terminal 1: Start server
python run.py

# Terminal 2: Open browser
http://localhost:5000/test-detection

# Click "Simulate Detection" to test
```

## 🔄 Switch Detection Mode

### Mock (Testing)
```bash
set DETECTION_MODE=mock
python run.py
```

### YOLOv8 (Real)
```bash
# Install once
python scripts/setup_yolov8.py

# Then run
set DETECTION_MODE=yolov8
python run.py
```

### Or Via API
```bash
# GET current mode
curl http://localhost:5000/api/system/detection-mode

# POST to switch
curl -X POST http://localhost:5000/api/system/detection-mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "yolov8"}'
```

## 📊 Quick API Reference

```bash
# Health check
curl http://localhost:5000/api/system/health

# System status
curl http://localhost:5000/api/system/status

# Get model info
curl http://localhost:5000/api/system/model-info

# Species list
curl http://localhost:5000/api/system/species-list

# Recent detections
curl http://localhost:5000/api/detections/recent

# Statistics
curl http://localhost:5000/api/detections/stats

# Upload image
curl -F "file=@image.jpg" \
     -F "latitude=-1.9441" \
     -F "longitude=30.0619" \
     http://localhost:5000/api/detections/upload

# Dashboard summary
curl http://localhost:5000/api/detections/dashboard-summary
```

## 🔧 Configuration

```bash
# Detection mode
set DETECTION_MODE=mock          # or yolov8

# Alert threshold (confidence %)
set ALERT_THRESHOLD=0.8

# Use GPU
set USE_GPU=true                 # or false

# Model size
set YOLOV8_MODEL=yolov8m.pt     # nano/small/medium/large/xlarge

# Detection threshold
set DETECTION_THRESHOLD=0.5
```

## 🧪 Testing

```bash
# Run full test suite
python scripts/test_detection_system.py

# Verify YOLOv8 installation
python scripts/setup_yolov8.py --verify

# Clear all detections
python scripts/clear_detections.py --remove-images -y

# Check Alembic state
python scripts/check_alembic_state.py
```

## 📁 Important Files

```
WildGuard_MVP/
├── run.py                           # Start server
├── requirements.txt                 # Dependencies
├── config/
│   ├── default.py                   # Config
│   └── detection_config.py           # Detection settings
├── app/
│   ├── models/
│   │   ├── detection.py            # Detection model
│   │   ├── alert.py                # Alert model
│   │   └── __init__.py             # Camera, Subscriber models
│   ├── services/
│   │   ├── detection_services.py   # Detection pipeline
│   │   ├── camera_service.py       # Camera management
│   │   └── notification_services.py # Alerts
│   ├── routes/
│   │   ├── detections_api.py       # 20+ API endpoints
│   │   ├── management.py           # System management
│   │   ├── alerts.py               # Alert handlers
│   │   └── pages.py                # Page routes
│   └── templates/
│       ├── test_detection.html      # Test dashboard
│       └── dashboard.html           # Main dashboard
├── ml/
│   ├── detector.py                 # Mock + YOLOv8
│   ├── species_classifier.py       # Species mapping
│   └── models/                     # Model storage
├── scripts/
│   ├── setup_yolov8.py            # Install YOLOv8
│   ├── test_detection_system.py   # Test suite
│   └── clear_detections.py        # Clean database
└── instance/
    └── wildguard.db               # SQLite database
```

## 🐛 Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| Server won't start | `netstat -ano \| findstr 5000` (kill process) |
| No module found | `pip install -r requirements.txt` |
| Database error | `flask db upgrade` |
| YOLOv8 not found | `python scripts/setup_yolov8.py` |
| Slow detection | `set USE_GPU=true` or use smaller model |
| Out of memory | `set YOLOV8_MODEL=yolov8n.pt` (nano) |

## 🗂️ Supported Species

```
🐘 Elephant      | 🦁 Lion         | 🐆 Leopard      | 🐃 Buffalo
🦒 Giraffe      | 🦓 Zebra        | 🦏 Rhino        | 🦛 Hippo
🐆 Cheetah      | 🐕 Wild Dog     | 🐕 Hyena        | 🦌 Antelope
🐄 Wildebeest   | 🦌 Deer         | 🐻 Bear         | 🐺 Wolf
```

## 🔗 Dashboard URLs

```
Main Dashboard:     http://localhost:5000/
Test Detection:     http://localhost:5000/test-detection
Detections Page:    http://localhost:5000/detections
About:              http://localhost:5000/about
Help:               http://localhost:5000/help
Contact:            http://localhost:5000/contact
```

## 💾 Database Schema

```sql
-- Detections
CREATE TABLE detections (
    id INTEGER PRIMARY KEY,
    species VARCHAR(50),
    confidence FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    camera_id VARCHAR(50),
    image_path VARCHAR(200),
    timestamp DATETIME,
    is_verified BOOLEAN,
    is_false_positive BOOLEAN
);

-- Cameras
CREATE TABLE camera (
    id INTEGER PRIMARY KEY,
    camera_id VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    is_active BOOLEAN,
    last_seen DATETIME
);

-- Alerts
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    detection_id INTEGER,
    alert_type VARCHAR(50),
    message TEXT,
    recipients VARCHAR(500),
    sms_sent BOOLEAN,
    email_sent BOOLEAN,
    timestamp DATETIME
);

-- Subscribers
CREATE TABLE subscriber (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    is_active BOOLEAN
);
```

## 🚀 Performance Tips

1. **Faster startup**: Use mock mode for development
2. **Better accuracy**: Use larger YOLOv8 model (`yolov8l.pt`)
3. **Faster inference**: Use GPU (`set USE_GPU=true`)
4. **Smaller model**: Use `yolov8n.pt` on low-end hardware
5. **Batch processing**: Upload multiple images at once

## 📚 Documentation

- Full guide: `IMPLEMENTATION_COMPLETE.md`
- YOLOv8 setup: `YOLOV8_SETUP.md`
- Project README: `README.md`

## 🎯 Common Commands

```bash
# Start development server
python run.py

# Run tests
python scripts/test_detection_system.py

# Install YOLOv8
python scripts/setup_yolov8.py

# Clear data
python scripts/clear_detections.py -y

# Check status
curl http://localhost:5000/api/system/status | python -m json.tool
```

---

**For detailed help:**
- Full docs: See `IMPLEMENTATION_COMPLETE.md`
- YOLOv8 guide: See `YOLOV8_SETUP.md`
- API reference: GET `http://localhost:5000/api/system/status`

🦁 **WildGuard - Protecting Wildlife with AI**
