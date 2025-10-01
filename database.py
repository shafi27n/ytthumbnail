from supabase import create_client
import logging

logger = logging.getLogger(__name__)

SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

class BotDatabase:
    def __init__(self):
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Supabase connected")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            self.client = None
    
    def save_bot_data(self, key: str, value: str):
        """Save bot-level data"""
        if not self.client:
            return False
        try:
            # Simple implementation - adjust based on your table structure
            result = self.client.table('bot_data').upsert({
                'key': key,
                'value': value
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving bot data: {e}")
            return False
    
    def save_user_data(self, user_id: int, key: str, value: str):
        """Save user-specific data"""
        if not self.client:
            return False
        try:
            result = self.client.table('user_data').upsert({
                'user_id': user_id,
                'key': key,
                'value': value
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: int, key: str, default=None):
        """Get user data"""
        if not self.client:
            return default
        try:
            result = self.client.table('user_data')\
                .select('value')\
                .eq('user_id', user_id)\
                .eq('key', key)\
                .execute()
            
            if result.data:
                return result.data[0]['value']
            return default
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return default

# Create global instance
db = BotDatabase()

# Shortcut functions
def Bot():
    from app import bot
    return bot

def User(user_id: int):
    return db