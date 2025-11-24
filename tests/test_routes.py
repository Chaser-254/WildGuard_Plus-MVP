import pytest
import json
from app import create_app, db
from app.models import Detection, Subscriber

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_receive_alert(client):
    """Test receiving an alert"""
    detection_data = {
        'species': 'elephant',
        'confidence': 0.95,
        'camera_id': 'cam_001',
        'location': {
            'lat': -1.9441,
            'lng': 30.0619
        }
    }
    
    response = client.post('/api/alert', 
                         json=detection_data,
                         content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'detection_id' in data

def test_get_detections(client):
    """Test getting detections"""
    response = client.get('/api/detections')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'detections' in data

def test_create_subscriber(client):
    """Test creating a subscriber"""
    subscriber_data = {
        'name': 'Test Ranger',
        'phone': '+254700000000',
        'email': 'test@example.com'
    }
    
    response = client.post('/api/subscribers',
                          json=subscriber_data,
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['subscriber']['name'] == 'Test Ranger'