import os
import requests
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedBotManager:
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}" if token else None
        self.user_sessions = {}
        self.pending_responses = {}
        logger.info("✅ Bot Manager initialized")
    
    def set_token(self, token: str):
        """Set bot token dynamically"""
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        logger.info(f"✅ Token set: {token[:10]}...")
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = 'HTML', **kwargs) -> dict:
        """Send message to Telegram"""
        if not self.token:
            return {'ok': False, 'error': 'Token not set'}
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        # Add optional parameters
        if 'reply_markup' in kwargs:
            payload['reply_markup'] = json.dumps(kwargs['reply_markup'])
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Send message error: {e}")
            return {'ok': False, 'error': str(e)}
    
    def handle_next_command(self, chat_id: int, expected_command: str, user_info: dict = None):
        """Setup next expected command"""
        self.pending_responses[chat_id] = {
            'expected_command': expected_command,
            'user_info': user_info or {},
            'timestamp': datetime.now()
        }
        logger.info(f"⏳ Waiting for {expected_command} from {chat_id}")
    
    def process_pending_response(self, chat_id: int, message_text: str, user_info: dict) -> str:
        """Process pending user response"""
        if chat_id in self.pending_responses:
            pending = self.pending_responses.pop(chat_id)
            expected_cmd = pending['expected_command']
            
            # Import and execute the expected command handler
            try:
                module_name = f"bot.handlers.{expected_cmd}"
                if expected_cmd == "demo_response":
                    module_name = "bot.handlers.utils_tools"
                
                module = __import__(module_name, fromlist=[''])
                handler_func = getattr(module, f"handle_{expected_cmd}")
                
                return handler_func(user_info, chat_id, message_text, bot_manager=self)
                
            except Exception as e:
                logger.error(f"Pending response error: {e}")
                return f"❌ Error processing response: {str(e)}"
        
        return None

# Global instance
bot_manager = AdvancedBotManager()
