import os
import requests
from flask import current_app

class SMSService:
    @staticmethod
    def send_sms(to_number, message):
        """
        Send SMS using Africa's Talking API
        """
        if not all([current_app.config.get('AFRICASTALKING_API_KEY'), 
                   current_app.config.get('AFRICASTALKING_USERNAME')]):
            current_app.logger.error("SMS service not configured")
            return False

        try:
            headers = {
                'ApiKey': current_app.config['AFRICASTALKING_API_KEY'],
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'username': current_app.config['AFRICASTALKING_USERNAME'],
                'to': to_number,
                'message': message,
                'from': 'WildGuard'
            }
            
            response = requests.post(
                'https://api.africastalking.com/version1/messaging',
                headers=headers,
                data=data
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send SMS: {str(e)}")
            return False