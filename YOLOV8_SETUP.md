# WildGuard YOLOv8 Detection System - Complete Guide

## Overview

WildGuard is a real-time wildlife detection system that can operate in two modes:

1. **Mock Mode** (Testing/Development) - No ML model required
2. **YOLOv8 Mode** (Production) - Real computer vision with YOLOv8

## Quick Start

### 1. Run in Mock Mode (Default)

```bash
python run.py
```

Visit: `http://localhost:5000/test-detection`

### 2. Install YOLOv8 (Option B)

Choose one installation method:

#### **Option A: CPU Only (Recommended for testing)**
```bash
python scripts/setup_yolov8.py
```

#### **Option B: GPU Support (CUDA)**
```bash
python scripts/setup_yolov8.py --gpu
```

#### **Option C: Conda (Easier for complex environments)**
```powershell
# Install from conda-forge (handles dependencies automatically)
conda install -c conda-forge ultralytics opencv pytorch::pytorch pytorch::torchvision pytorch::torchaudio pytorch::pytorch-cuda=12.1
```

### 3. Switch to YOLOv8 Mode

**Option 1: Environment Variable**
```bash
set DETECTION_MODE=yolov8
python run.py
```

**Option 2: API Endpoint**
```bash
curl -X POST http://localhost:5000/api/system/detection-mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "yolov8"}'
```

**Option 3: Code**
```python
from app.services.detection_services import detection_service
detection_service.switch_mode(use_mock=False)
```

## Supported Wildlife Species (14+)

- 🐘 **Elephant** - Threat Level: Medium
- 🦁 **Lion** - Threat Level: High
- 🐆 **Leopard** - Threat Level: High
- 🐃 **Buffalo** - Threat Level: High
- 🦒 **Giraffe** - Threat Level: Low
- 🦓 **Zebra** - Threat Level: Low
- 🦏 **Rhino** - Threat Level: High
- 🦛 **Hippo** - Threat Level: High
- 🐆 **Cheetah** - Threat Level: High
- 🐕 **Hyena** - Threat Level: Medium
- 🐦 **Wild Dog** - Threat Level: High
- 🦌 **Antelope** - Threat Level: Low
- 🐄 **Wildebeest** - Threat Level: Low

## Key API Endpoints

```
# Detection
POST   /api/detections/upload                  - Upload image and run detection
GET    /api/detections/recent                  - Get recent detections
GET    /api/detections/stats                   - Statistics by species
GET    /api/detections/dashboard-summary       - Complete dashboard data

# System Management
GET    /api/system/status                      - System status
GET    /api/system/detection-mode              - Current mode (mock/yolov8)
POST   /api/system/detection-mode              - Switch mode
GET    /api/system/model-info                  - Model information
GET    /api/system/health                      - Health check
```

## Configuration

Edit `config/detection_config.py` or set environment variables:

```bash
set DETECTION_MODE=yolov8          # Switch to real YOLOv8
set ALERT_THRESHOLD=0.8             # Minimum confidence for alerts (80%)
set USE_GPU=true                    # Enable GPU acceleration
set YOLOV8_MODEL=yolov8m.pt        # Model size: nano/small/medium/large/xlarge
```

## Installation Steps

### Step 1: Verify Python Environment
```powershell
python --version
pip --version
```

### Step 2: Run Setup Script
```powershell
# For CPU (faster setup)
python scripts/setup_yolov8.py

# For GPU (if you have CUDA)
python scripts/setup_yolov8.py --gpu
```

### Step 3: Verify Installation
```powershell
python scripts/setup_yolov8.py --verify
```

### Step 4: Test the System
```powershell
# Set detection mode to YOLOv8
set DETECTION_MODE=yolov8

# Start server
python run.py

# Visit in browser: http://localhost:5000/test-detection
```

### Step 5: Upload Test Image
```bash
curl -F "file=@path/to/image.jpg" \
     -F "latitude=-1.9441" \
     -F "longitude=30.0619" \
     http://localhost:5000/api/detections/upload
```

## Performance Metrics

| Mode | Speed (CPU) | Speed (GPU) | RAM | Accuracy |
|------|-----------|-----------|-----|----------|
| Mock | <10ms | N/A | <50MB | Simulated 75-99% |
| YOLOv8n | ~200ms | ~50ms | 500MB | Real |
| YOLOv8m | ~300ms | ~80ms | 1GB | Real |
| YOLOv8l | ~500ms | ~150ms | 2GB | Real |

## Troubleshooting

### "ModuleNotFoundError: No module named 'ultralytics'"
```powershell
python scripts/setup_yolov8.py
```

### "CUDA out of memory"
```powershell
set USE_GPU=false
set YOLOV8_MODEL=yolov8n.pt
```

### "No detections found"
```powershell
set DETECTION_THRESHOLD=0.3  # Lower threshold
```

### Slow on CPU
```powershell
set USE_GPU=true   # Use GPU if available
```

---

**Next Steps:**
1. Run mock tests to verify infrastructure works
2. Install YOLOv8 using setup script
3. Switch to real detection mode
4. Upload wildlife images for testing
5. Monitor detection accuracy and adjust thresholds

For detailed documentation, see: README.md
