# Camera Streams - WildGuard Detection

This document explains the camera stream functionality added to the WildGuard MVP.

## Overview

You can register RTSP/HTTP camera streams and the server will pull frames periodically and run detections on them (mock by default).

Endpoints
- `GET /api/streams` - list active streams
- `POST /api/streams` - register and start a stream
  - Body JSON: `{ "id": "cam_01", "url": "rtsp://...", "interval": 5.0, "use_mock": true }`
- `DELETE /api/streams/<id>` - stop and remove stream

## How it works
- Each registered stream spawns a `StreamWorker` thread that opens the camera with OpenCV and periodically captures frames.
- Frames are saved to `tmp_stream_frames/` briefly and passed through `DetectionService.process_image` for inference and storage.
- The detection service is mocked by default; install YOLOv8 and switch mode to `use_mock=false` to run real inference.

## Configuration
- `interval` controls how often (in seconds) the worker captures a frame and runs detection. Default is 5s.
- Workers run as daemon threads; they stop when removed or when the app exits.

## Notes and Safety
- Streaming many cameras concurrently can be resource-intensive. Keep `interval` reasonable (>= 3s) and limit concurrent streams.
- For production, run stream workers in a dedicated worker process or use a message queue (Celery/RQ) and avoid in-process threads.
- Temporary frames are stored in `tmp_stream_frames/`. The worker attempts to delete them after processing.

## Example
Start a stream (mock mode):

```bash
curl -X POST http://localhost:5000/api/streams -H "Content-Type: application/json" \
  -d '{"id":"cam_demo","url":"/path/to/sample_video.mp4","interval":4.0,"use_mock":true}'
```

List streams:

```bash
curl http://localhost:5000/api/streams
```

Stop a stream:

```bash
curl -X DELETE http://localhost:5000/api/streams/cam_demo
```
