#!/usr/bin/env python3
"""
Database setup script for ElephantAI Alert System
"""
import os
import sys

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Camera, Subscriber

def setup_database():
    """Initialize the database with default data"""
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Add default cameras
        cameras = [
            {'camera_id': 'cam_001', 'name': 'Main Waterhole', 'latitude': -1.9441, 'longitude': 30.0619},
            {'camera_id': 'cam_002', 'name': 'Northern Corridor', 'latitude': -1.9500, 'longitude': 30.0700},
            {'camera_id': 'cam_003', 'name': 'Southern Border', 'latitude': -1.9300, 'longitude': 30.0500},
        ]
        
        for cam_data in cameras:
            if not Camera.query.filter_by(camera_id=cam_data['camera_id']).first():
                camera = Camera(**cam_data)
                db.session.add(camera)
                print(f"✅ Added camera: {cam_data['name']}")
        
        # Add sample subscribers
        subscribers = [
            {'name': 'Head Ranger', 'phone': '+254700000001', 'email': 'ranger@example.com'},
            {'name': 'Community Leader', 'phone': '+254700000002', 'email': 'community@example.com'},
            {'name': 'Wildlife Warden', 'phone': '+254700000003', 'email': 'warden@example.com'},
        ]
        
        for sub_data in subscribers:
            if not Subscriber.query.filter_by(phone=sub_data['phone']).first():
                subscriber = Subscriber(**sub_data)
                db.session.add(subscriber)
                print(f"✅ Added subscriber: {sub_data['name']}")
        
        db.session.commit()
        print("✅ Database setup completed successfully!")
        
        # Print summary
        print(f"\n📊 Database Summary:")
        print(f"   Cameras: {Camera.query.count()}")
        print(f"   Subscribers: {Subscriber.query.filter_by(is_active=True).count()}")

if __name__ == '__main__':
    setup_database()