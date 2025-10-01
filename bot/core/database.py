import os
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    
    def __init__(self):
        self.supabase: Client = None
        self.initialize()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self):
        try:
            url = os.environ.get('SUPABASE_URL', 'https://megohojyelqspypejlpo.supabase.co')
            key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo')
            
            self.supabase = create_client(url, key)
            logger.info("✅ Supabase connection initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            self.supabase = None
    
    def save_bot_data(self, variable: str, value: str):
        """Save data for all users (bot-level data)"""
        try:
            if not self.supabase:
                return False
            
            result = self.supabase.table('bot_data').upsert({
                'variable': variable,
                'value': value,
                'updated_at': 'now()'
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Error saving bot data: {e}")
            return False
    
    def get_bot_data(self, variable: str):
        """Get bot-level data"""
        try:
            if not self.supabase:
                return None
            
            result = self.supabase.table('bot_data').select('*').eq('variable', variable).execute()
            return result.data[0]['value'] if result.data else None
        except Exception as e:
            logger.error(f"❌ Error getting bot data: {e}")
            return None
    
    def save_user_data(self, user_id: int, variable: str, value: str):
        """Save data for specific user"""
        try:
            if not self.supabase:
                return False
            
            result = self.supabase.table('user_data').upsert({
                'user_id': user_id,
                'variable': variable,
                'value': value,
                'updated_at': 'now()'
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: int, variable: str):
        """Get user-specific data"""
        try:
            if not self.supabase:
                return None
            
            result = self.supabase.table('user_data').select('*').eq('user_id', user_id).eq('variable', variable).execute()
            return result.data[0]['value'] if result.data else None
        except Exception as e:
            logger.error(f"❌ Error getting user data: {e}")
            return None
    
    def get_all_user_data(self, user_id: int):
        """Get all data for a user"""
        try:
            if not self.supabase:
                return {}
            
            result = self.supabase.table('user_data').select('*').eq('user_id', user_id).execute()
            return {item['variable']: item['value'] for item in result.data}
        except Exception as e:
            logger.error(f"❌ Error getting all user data: {e}")
            return {}
