from flask import Blueprint, request, jsonify, current_app

config_bp = Blueprint('config', __name__)

@config_bp.route('/config', methods=['GET'])
def get_config():
    cfg = {
        'DETECTION_CONF_THRESHOLD': current_app.config.get('DETECTION_CONF_THRESHOLD', 0.5),
        'STREAM_INTERVAL_DEFAULT': current_app.config.get('STREAM_INTERVAL_DEFAULT', 5.0),
        'DETECTION_USE_MOCK': current_app.config.get('DETECTION_USE_MOCK', True)
    }
    return jsonify(cfg)

@config_bp.route('/config', methods=['POST'])
def set_config():
    data = request.get_json() or {}
    # Allowed keys
    allowed = ['DETECTION_CONF_THRESHOLD', 'STREAM_INTERVAL_DEFAULT', 'DETECTION_USE_MOCK']
    updated = {}
    for k in allowed:
        if k in data:
            current_app.config[k] = data[k]
            updated[k] = data[k]
    if not updated:
        return jsonify({'status': 'error', 'message': 'No valid config keys provided'}), 400
    return jsonify({'status': 'success', 'updated': updated}), 200
