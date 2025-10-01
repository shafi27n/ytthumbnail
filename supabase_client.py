import requests
import json
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.url = 'https://megohojyelqspypejlpo.supabase.co'
        self.key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
    
    def user_save_data(self, user_id, variable, value):
        """Save user data to Supabase"""
        try:
            data = {
                'user_id': user_id,
                'variable': variable,
                'value': value
            }
            
            response = requests.post(
                f'{self.url}/rest/v1/user_data',
                headers=self.headers,
                json=data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ User data saved: {user_id} - {variable} = {value}")
                return True
            else:
                logger.error(f"❌ User data save failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ User save error: {e}")
            return False
    
    def user_get_data(self, user_id, variable):
        """Get user data from Supabase"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/user_data?user_id=eq.{user_id}&variable=eq.{variable}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return data[0].get('value')
            return None
            
        except Exception as e:
            logger.error(f"❌ User get error: {e}")
            return None
    
    def user_get_all_data(self, user_id):
        """Get all data for a user"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/user_data?user_id=eq.{user_id}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            logger.error(f"❌ User get all error: {e}")
            return []
    
    def bot_save_data(self, variable, value):
        """Save bot data to Supabase"""
        try:
            data = {
                'variable': variable,
                'value': value
            }
            
            response = requests.post(
                f'{self.url}/rest/v1/bot_data',
                headers=self.headers,
                json=data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Bot data saved: {variable} = {value}")
                return True
            else:
                logger.error(f"❌ Bot data save failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Bot save error: {e}")
            return False
    
    def bot_get_data(self, variable):
        """Get bot data from Supabase"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/bot_data?variable=eq.{variable}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return data[0].get('value')
            return None
            
        except Exception as e:
            logger.error(f"❌ Bot get error: {e}")
            return None
    
    def delete_user_data(self, user_id, variable=None):
        """Delete user data"""
        try:
            if variable:
                url = f'{self.url}/rest/v1/user_data?user_id=eq.{user_id}&variable=eq.{variable}'
            else:
                url = f'{self.url}/rest/v1/user_data?user_id=eq.{user_id}'
            
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ User data deleted: {user_id} - {variable}")
                return True
            else:
                logger.error(f"❌ User data delete failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ User delete error: {e}")
            return False

# Global Supabase client instance
supabase = SupabaseClient()
