import os
import requests
import json
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedBotManager:
    def __init__(self, token: str = None):
        self.token = token or os.environ.get('BOT_TOKEN')
        if self.token:
            self.base_url = f"https://api.telegram.org/bot{self.token}"
        else:
            self.base_url = None
        self.user_sessions = {}
        self.pending_responses = {}
    
    def set_token(self, token: str):
        """Set bot token dynamically"""
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    # Basic message methods (most essential)
    def send_message(self, chat_id: int, text: str, parse_mode: str = 'HTML', **kwargs) -> Dict:
        """Send text message"""
        if not self.base_url:
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
            logger.error(f"Error sending message: {e}")
            return {'ok': False, 'error': str(e)}
    
    def run_command(self, command_name: str, user_info: Dict, chat_id: int, message_text: str, **kwargs) -> str:
        """Execute a specific command by name"""
        try:
            # Remove slash if present
            clean_name = command_name.replace('/', '')
            module_name = f"bot.handlers.{clean_name}"
            
            # Dynamic import
            module = __import__(module_name, fromlist=[''])
            handler_func = getattr(module, f"handle_{clean_name}")
            
            return handler_func(user_info, chat_id, message_text, bot_manager=self, **kwargs)
        except Exception as e:
            logger.error(f"Error running command {command_name}: {e}")
            return f"❌ Error executing command: {str(e)}"
    
    def handle_next_command(self, chat_id: int, expected_command: str, user_info: Dict = None):
        """Set up expectation for next user response"""
        self.pending_responses[chat_id] = {
            'expected_command': expected_command,
            'user_info': user_info or {},
            'timestamp': datetime.now()
        }
    
    def process_pending_response(self, chat_id: int, message_text: str, user_info: Dict) -> Optional[str]:
        """Process user response for pending command"""
        if chat_id in self.pending_responses:
            pending = self.pending_responses.pop(chat_id)
            command_name = pending['expected_command']
            return self.run_command(command_name, user_info, chat_id, message_text, is_pending_response=True)
        return None

# Global instance
bot_manager = AdvancedBotManager()
