from flask import Blueprint, request, jsonify
from app import db
from app.models import Subscriber
import re

subscribers_bp = Blueprint('subscribers', __name__)

@subscribers_bp.route('/subscribers', methods=['GET'])
def get_subscribers():
    try:
        subscribers = Subscriber.query.filter_by(is_active=True).all()
        return jsonify({
            'status': 'success',
            'count': len(subscribers),
            'subscribers': [sub.to_dict() for sub in subscribers]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@subscribers_bp.route('/subscribers', methods=['POST'])
def create_subscriber():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not (data.get('phone') or data.get('email')):
            return jsonify({
                'status': 'error',
                'message': 'Name and at least one contact method (phone or email) are required'
            }), 400
        
        # Check for existing subscriber
        existing = None
        if data.get('phone'):
            existing = Subscriber.query.filter_by(phone=data['phone']).first()
        elif data.get('email'):
            existing = Subscriber.query.filter_by(email=data['email']).first()
        
        if existing:
            existing.is_active = True
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Subscriber reactivated',
                'subscriber': existing.to_dict()
            }), 200
        
        # Create new subscriber
        subscriber = Subscriber(
            name=data['name'],
            phone=data.get('phone'),
            email=data.get('email')
        )
        
        db.session.add(subscriber)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Subscriber created',
            'subscriber': subscriber.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@subscribers_bp.route('/subscribers/<int:subscriber_id>', methods=['DELETE'])
def delete_subscriber(subscriber_id):
    try:
        subscriber = Subscriber.query.get_or_404(subscriber_id)
        subscriber.is_active = False
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Subscriber deactivated'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400