import os
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models import Subscriber
from app import db

def send_sms(message, to_number):
    """Send SMS using Twilio"""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if all([account_sid, auth_token, from_number]):
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            print(f"SMS sent to {to_number}: {message.sid}")
            return True
        else:
            print(f"Mock SMS: {message} to {to_number}")
            return True
            
    except Exception as e:
        print(f"SMS failed: {e}")
        return False

def send_notifications(detection):
    """Send all notifications for a detection"""
    message = f"ELEPHANT DETECTED!\nCamera: {detection.camera_id}\nConfidence: {detection.confidence:.1%}\nLocation: {detection.latitude:.4f}, {detection.longitude:.4f}\nTime: {detection.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    email_subject = f"Elephant Detection Alert - Camera {detection.camera_id}"
    email_body = f"""
Elephant Detection Alert System

ALERT: Elephant detected!
- Camera: {detection.camera_id}
- Confidence: {detection.confidence:.1%}
- Location: {detection.latitude:.4f}, {detection.longitude:.4f}
- Time: {detection.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Please check the dashboard for more details: http://localhost:5000

Stay safe,
ElephantAI Alert System
"""
    
    # Get active subscribers from database
    subscribers = Subscriber.query.filter_by(is_active=True).all()
    
    notifications_sent = 0
    
    for subscriber in subscribers:
        success = False
        if subscriber.phone:
            success = send_sms(message, subscriber.phone)
        elif subscriber.email:
            success = send_email(email_subject, email_body, subscriber.email)
        
        if success:
            notifications_sent += 1
    
    print(f"Notifications sent: {notifications_sent}/{len(subscribers)}")
    return notifications_sent