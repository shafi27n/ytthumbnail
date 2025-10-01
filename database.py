import requests
import logging

logger = logging.getLogger(__name__)

SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

class BotDatabase:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'apikey': self.key
        }
        logger.info("✅ Database initialized")
    
    def save_bot_data(self, key, value):
        """Save bot data using Supabase REST API"""
        try:
            data = {
                'key': key,
                'value': value
            }
            response = requests.post(
                f'{self.url}/rest/v1/bot_data',
                headers=self.headers,
                json=data
            )
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Error saving bot data: {e}")
            return False
    
    def save_user_data(self, user_id, key, value):
        """Save user data using Supabase REST API"""
        try:
            data = {
                'user_id': user_id,
                'key': key,
                'value': value
            }
            response = requests.post(
                f'{self.url}/rest/v1/user_data',
                headers=self.headers,
                json=data
            )
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id, key, default=None):
        """Get user data"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/user_data?user_id=eq.{user_id}&key=eq.{key}',
                headers=self.headers
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]['value']
            return default
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return default

# Global instance
db = BotDatabase()