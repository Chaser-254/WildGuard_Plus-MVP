from flask import Blueprint, request, jsonify, current_app
from app import db, socketio
from app.models import Detection
from app.services.notification_services import send_notifications
import random
from datetime import datetime


alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('/alert', methods=['POST'])
def receive_alert():
    try:
        data = request.json

        # Create new detection (use provided location)
        detection = Detection(
            species=data.get('species', 'elephant'),
            confidence=data.get('confidence', 0.0),
            camera_id=data.get('camera_id', 'unknown'),
            latitude=data['location']['lat'],
            longitude=data['location']['lng'],
            image_path=data.get('image_path')
        )

        db.session.add(detection)
        db.session.commit()

        # Emit via socketio so UI updates immediately
        try:
            socketio.emit('new_detection', detection.to_dict(), namespace='/')
        except Exception:
            current_app.logger.exception('Failed to emit new_detection')

        # Send notifications (SMS / email) and return count
        notifications_sent = send_notifications(detection)

        return jsonify({
            'status': 'success',
            'message': 'Alert processed',
            'detection_id': detection.id,
            'notifications_sent': notifications_sent
        }), 201

    except Exception as e:
        current_app.logger.exception('Error processing alert')
        return jsonify({'status': 'error', 'message': str(e)}), 400


@alerts_bp.route('/alert/simulate', methods=['POST', 'GET'])
def simulate_alert():
    """Create a simple simulated elephant detection, notify subscribers,
    emit socket event and return the created detection."""
    try:
        # Choose a base location near map center (Taita Taveta center used in frontend)
        base_lat = -3.3962
        base_lng = 38.5569

        # Small random offset
        lat = base_lat + (random.random() - 0.5) * 0.02
        lng = base_lng + (random.random() - 0.5) * 0.02

        confidence = round(random.uniform(0.85, 0.98), 2)

        # Prepare data for insertion, but be schema-safe: only insert columns that exist
        # Query table columns
        conn = db.engine.raw_connection()
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(detections);")
        cols = [row[1] for row in cur.fetchall()]

        # Build values dict
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        values = {
            'species': 'elephant',
            'confidence': confidence,
            'latitude': lat,
            'longitude': lng,
            'timestamp': now,
            'image_path': None,
            'is_verified': 0,
            'is_false_positive': 0,
            'camera_id': 'sim_cam'
        }

        insert_keys = [k for k in ['species','confidence','camera_id','latitude','longitude','timestamp','image_path','is_verified','is_false_positive'] if k in cols]
        insert_vals = [values[k] for k in insert_keys]

        placeholders = ','.join(['?'] * len(insert_keys))
        sql = f"INSERT INTO detections ({','.join(insert_keys)}) VALUES ({placeholders})"
        cur.execute(sql, insert_vals)
        conn.commit()
        detection_id = cur.lastrowid
        cur.close()
        conn.close()

        # Load the newly created detection via the ORM (safe even if some columns were omitted)
        detection = Detection.query.get(detection_id)

        # Emit and notify
        try:
            socketio.emit('new_detection', detection.to_dict(), namespace='/')
        except Exception:
            current_app.logger.exception('Failed to emit simulated new_detection')

        notifications_sent = send_notifications(detection)

        return jsonify({'status':'success','detection': detection.to_dict(), 'notifications_sent': notifications_sent}), 201

    except Exception as e:
        current_app.logger.exception('Error simulating alert')
        return jsonify({'status':'error','message': str(e)}), 500