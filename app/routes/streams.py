from flask import Blueprint, request, jsonify, current_app
from app.services.stream_service import get_stream_manager

streams_bp = Blueprint('streams', __name__)

@streams_bp.route('/streams', methods=['GET'])
def list_streams():
    manager = get_stream_manager()
    return jsonify({'streams': manager.list_streams()})

@streams_bp.route('/streams', methods=['POST'])
def add_stream():
    data = request.get_json() or {}
    stream_id = data.get('id')
    url = data.get('url')
    interval = float(data.get('interval', 5.0))
    use_mock = bool(data.get('use_mock', True))

    if not stream_id or not url:
        return jsonify({'status': 'error', 'message': 'Missing id or url'}), 400

    manager = get_stream_manager()
    ok = manager.add_stream(stream_id, url, interval=interval, use_mock=use_mock)
    if ok:
        return jsonify({'status': 'success', 'message': f'Started stream {stream_id}'}), 201
    return jsonify({'status': 'error', 'message': 'Stream already exists'}), 400

@streams_bp.route('/streams/<stream_id>', methods=['DELETE'])
def remove_stream(stream_id):
    manager = get_stream_manager()
    ok = manager.remove_stream(stream_id)
    if ok:
        return jsonify({'status': 'success', 'message': f'Stopped stream {stream_id}'}), 200
    return jsonify({'status': 'error', 'message': 'Stream not found'}), 404
