from supabase import create_client

SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

class BotDatabase:
    def __init__(self):
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except:
            self.client = None
    
    def save_bot_data(self, key, value):
        """Save data for all users"""
        if not self.client:
            return False
        try:
            # Implement based on your table structure
            return True
        except:
            return False
    
    def save_user_data(self, user_id, key, value):
        """Save user-specific data"""
        if not self.client:
            return False
        try:
            # Implement based on your table structure
            return True
        except:
            return False
    
    def get_user_data(self, user_id, key, default=None):
        """Get user data"""
        if not self.client:
            return default
        try:
            # Implement based on your table structure
            return default
        except:
            return default
