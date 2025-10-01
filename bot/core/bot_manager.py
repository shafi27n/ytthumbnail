import os
import logging
import importlib
import pkgutil
from typing import Dict, Any, Callable, Optional
import requests
from .database import Database

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.db = Database.get_instance()
        self.waiting_commands: Dict[int, str] = {}  # user_id -> command
        self.command_handlers: Dict[str, Callable] = {}
        self.bot_token = os.environ.get('BOT_TOKEN', '')  # Optional from env
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
        
    def auto_discover_handlers(self):
        """Automatically discover all handler modules"""
        handlers = {}
        
        try:
            handlers_package = importlib.import_module('bot.handlers')
            
            for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
                if module_name != '__init__':
                    try:
                        module = importlib.import_module(f'bot.handlers.{module_name}')
                        
                        # Handle multiple command names (name1|name2|name3.py)
                        command_names = module_name.split('|')
                        
                        for cmd_name in command_names:
                            function_name = f"handle_{cmd_name}"
                            if hasattr(module, function_name):
                                command_name = f"/{cmd_name}"
                                handlers[command_name] = getattr(module, function_name)
                                logger.info(f"✅ Auto-loaded command: {command_name}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error loading handler {module_name}: {e}")
        
        except Exception as e:
            logger.error(f"❌ Error discovering handlers: {e}")
        
        self.command_handlers = handlers
        return handlers
    
    def set_token(self, token: str):
        """Set bot token dynamically"""
        self.bot_token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        logger.info("✅ Bot token set dynamically")
    
    def run_command(self, command_name: str, user_info: Dict, chat_id: int, message_text: str) -> str:
        """Execute a specific command"""
        try:
            if command_name in self.command_handlers:
                return self.command_handlers[command_name](user_info, chat_id, message_text, self)
            else:
                return f"❌ Command '{command_name}' not found"
        except Exception as e:
            error_msg = f"❌ Error executing command '{command_name}': {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def handle_next_command(self, user_id: int, next_command: str):
        """Set next command to wait for user response"""
        self.waiting_commands[user_id] = next_command
        return True
    
    def get_waiting_command(self, user_id: int) -> Optional[str]:
        """Get waiting command for user"""
        return self.waiting_commands.pop(user_id, None)
    
    def save_data(self, variable: str, value: str) -> bool:
        """Save data for all users"""
        return self.db.save_bot_data(variable, value)
    
    def get_data(self, variable: str) -> Optional[str]:
        """Get bot-level data"""
        return self.db.get_bot_data(variable)
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = 'HTML', 
                   reply_markup: Optional[Dict] = None) -> bool:
        """Send message to Telegram"""
        try:
            if not self.bot_token:
                logger.error("❌ Bot token not set")
                return False
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            if reply_markup:
                payload['reply_markup'] = reply_markup
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False
    
    # ... (other methods remain the same as previous version)
    def edit_message(self, chat_id: int, message_id: int, text: str, 
                    parse_mode: str = 'HTML', reply_markup: Optional[Dict] = None) -> bool:
        """Edit existing message"""
        try:
            if not self.bot_token:
                logger.error("❌ Bot token not set")
                return False
            
            url = f"{self.base_url}/editMessageText"
            payload = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            if reply_markup:
                payload['reply_markup'] = reply_markup
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Error editing message: {e}")
            return False
    
    def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete message"""
        try:
            if not self.bot_token:
                logger.error("❌ Bot token not set")
                return False
            
            url = f"{self.base_url}/deleteMessage"
            payload = {
                'chat_id': chat_id,
                'message_id': message_id
            }
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Error deleting message: {e}")
            return False
    
    def send_photo(self, chat_id: int, photo_url: str, caption: str = "", 
                  parse_mode: str = 'HTML') -> bool:
        """Send photo"""
        try:
            if not self.bot_token:
                logger.error("❌ Bot token not set")
                return False
            
            url = f"{self.base_url}/sendPhoto"
            payload = {
                'chat_id': chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Error sending photo: {e}")
            return False
    
    def send_video(self, chat_id: int, video_url: str, caption: str = "", 
                  parse_mode: str = 'HTML') -> bool:
        """Send video"""
        try:
            if not self.bot_token:
                logger.error("❌ Bot token not set")
                return False
            
            url = f"{self.base_url}/sendVideo"
            payload = {
                'chat_id': chat_id,
                'video': video_url,
                'caption': caption,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Error sending video: {e}")
            return False
    
    def make_http_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request"""
        try:
            if method.upper() == 'GET':
                response = requests.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, **kwargs)
            else:
                return None
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'text': response.text,
                'json': response.json() if response.headers.get('content-type') == 'application/json' else None
            }
        except Exception as e:
            logger.error(f"❌ HTTP request error: {e}")
            return None

class UserManager:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = Database.get_instance()
    
    def save_data(self, variable: str, value: str) -> bool:
        """Save user-specific data"""
        return self.db.save_user_data(self.user_id, variable, value)
    
    def get_data(self, variable: str) -> Optional[str]:
        """Get user-specific data"""
        return self.db.get_user_data(self.user_id, variable)
    
    def get_all_data(self) -> Dict[str, str]:
        """Get all user data"""
        return self.db.get_all_user_data(self.user_id)
