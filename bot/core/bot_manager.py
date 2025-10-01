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
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.user_sessions = {}  # Store user states and data
        self.pending_responses = {}  # Store pending user responses
    
    def set_token(self, token: str):
        """Set bot token dynamically"""
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def run_command(self, command_name: str, user_info: Dict, chat_id: int, message_text: str, **kwargs) -> str:
        """Execute a specific command by name"""
        try:
            # Import and execute command dynamically
            module_name = f"bot.handlers.{command_name.replace('/', '')}"
            module = __import__(module_name, fromlist=[''])
            handler_func = getattr(module, f"handle_{command_name.replace('/', '')}")
            
            # Pass bot_manager instance to handler
            return handler_func(user_info, chat_id, message_text, bot_manager=self, **kwargs)
        except Exception as e:
            logger.error(f"Error running command {command_name}: {e}")
            return f"❌ Error executing command: {str(e)}"
    
    def handle_next_command(self, chat_id: int, expected_command: str, user_info: Dict = None):
        """Set up expectation for next user response"""
        self.pending_responses[chat_id] = {
            'expected_command': expected_command,
            'user_info': user_info,
            'timestamp': datetime.now()
        }
    
    def process_pending_response(self, chat_id: int, message_text: str, user_info: Dict) -> Optional[str]:
        """Process user response for pending command"""
        if chat_id in self.pending_responses:
            pending = self.pending_responses.pop(chat_id)
            command_name = pending['expected_command']
            return self.run_command(command_name, user_info, chat_id, message_text, is_pending_response=True)
        return None
    
    # 🔧 CORE MESSAGE METHODS
    
    def send_message(
        self, 
        chat_id: int, 
        text: str, 
        parse_mode: str = 'HTML',
        reply_markup: Dict = None,
        reply_to_message_id: int = None,
        disable_web_page_preview: bool = None
    ) -> Dict:
        """Send text message with advanced options"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        if reply_to_message_id:
            payload['reply_to_message_id'] = reply_to_message_id
        if disable_web_page_preview is not None:
            payload['disable_web_page_preview'] = disable_web_page_preview
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = 'HTML',
        reply_markup: Dict = None
    ) -> Dict:
        """Edit existing message text"""
        url = f"{self.base_url}/editMessageText"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def delete_message(self, chat_id: int, message_id: int) -> Dict:
        """Delete a message"""
        url = f"{self.base_url}/deleteMessage"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        
        response = requests.post(url, json=payload)
        return response.json()
    
    # 📷 MEDIA METHODS
    
    def send_photo(
        self,
        chat_id: int,
        photo: Union[str, bytes],
        caption: str = None,
        parse_mode: str = 'HTML',
        reply_markup: Dict = None
    ) -> Dict:
        """Send photo with caption"""
        url = f"{self.base_url}/sendPhoto"
        
        if isinstance(photo, str) and photo.startswith(('http://', 'https://')):
            # Photo from URL
            payload = {
                'chat_id': chat_id,
                'photo': photo
            }
        else:
            # Photo from file
            files = {'photo': photo}
            payload = {'chat_id': chat_id}
            response = requests.post(url, files=files, data=payload)
            return response.json()
        
        if caption:
            payload['caption'] = caption
            payload['parse_mode'] = parse_mode
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def send_video(
        self,
        chat_id: int,
        video: Union[str, bytes],
        caption: str = None,
        parse_mode: str = 'HTML',
        reply_markup: Dict = None
    ) -> Dict:
        """Send video with caption"""
        url = f"{self.base_url}/sendVideo"
        
        if isinstance(video, str) and video.startswith(('http://', 'https://')):
            payload = {
                'chat_id': chat_id,
                'video': video
            }
        else:
            files = {'video': video}
            payload = {'chat_id': chat_id}
            response = requests.post(url, files=files, data=payload)
            return response.json()
        
        if caption:
            payload['caption'] = caption
            payload['parse_mode'] = parse_mode
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def send_document(
        self,
        chat_id: int,
        document: Union[str, bytes],
        caption: str = None,
        parse_mode: str = 'HTML',
        reply_markup: Dict = None
    ) -> Dict:
        """Send document with caption"""
        url = f"{self.base_url}/sendDocument"
        
        if isinstance(document, str) and document.startswith(('http://', 'https://')):
            payload = {
                'chat_id': chat_id,
                'document': document
            }
        else:
            files = {'document': document}
            payload = {'chat_id': chat_id}
            response = requests.post(url, files=files, data=payload)
            return response.json()
        
        if caption:
            payload['caption'] = caption
            payload['parse_mode'] = parse_mode
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(url, json=payload)
        return response.json()
    
    # 🎛️ KEYBOARD METHODS
    
    def create_reply_keyboard(
        self,
        keyboard: List[List[Dict]],
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
        selective: bool = None
    ) -> Dict:
        """Create custom reply keyboard"""
        markup = {
            'keyboard': keyboard,
            'resize_keyboard': resize_keyboard,
            'one_time_keyboard': one_time_keyboard
        }
        
        if selective is not None:
            markup['selective'] = selective
        
        return markup
    
    def create_inline_keyboard(self, keyboard: List[List[Dict]]) -> Dict:
        """Create inline keyboard"""
        return {
            'inline_keyboard': keyboard
        }
    
    def create_keyboard_button(self, text: str, **kwargs) -> Dict:
        """Create keyboard button with various options"""
        button = {'text': text}
        
        if 'request_contact' in kwargs:
            button['request_contact'] = kwargs['request_contact']
        if 'request_location' in kwargs:
            button['request_location'] = kwargs['request_location']
        if 'web_app' in kwargs:
            button['web_app'] = kwargs['web_app']
        
        return button
    
    def create_inline_button(self, text: str, **kwargs) -> Dict:
        """Create inline button with various options"""
        button = {'text': text}
        
        if 'url' in kwargs:
            button['url'] = kwargs['url']
        elif 'callback_data' in kwargs:
            button['callback_data'] = kwargs['callback_data']
        elif 'switch_inline_query' in kwargs:
            button['switch_inline_query'] = kwargs['switch_inline_query']
        elif 'switch_inline_query_current_chat' in kwargs:
            button['switch_inline_query_current_chat'] = kwargs['switch_inline_query_current_chat']
        elif 'pay' in kwargs:
            button['pay'] = kwargs['pay']
        
        return button
    
    def remove_reply_keyboard(self, selective: bool = None) -> Dict:
        """Remove reply keyboard"""
        markup = {
            'remove_keyboard': True
        }
        
        if selective is not None:
            markup['selective'] = selective
        
        return markup
    
    # 🌐 HTTP REQUEST METHODS
    
    def http_get(self, url: str, headers: Dict = None, params: Dict = None) -> Dict:
        """Perform HTTP GET request"""
        try:
            response = requests.get(url, headers=headers, params=params)
            return {
                'success': True,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'json': response.json() if response.headers.get('content-type') == 'application/json' else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def http_post(self, url: str, data: Dict = None, json_data: Dict = None, headers: Dict = None) -> Dict:
        """Perform HTTP POST request"""
        try:
            response = requests.post(url, data=data, json=json_data, headers=headers)
            return {
                'success': True,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'json': response.json() if response.headers.get('content-type') == 'application/json' else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # 🔔 CALLBACK QUERY METHODS
    
    def answer_callback_query(
        self,
        callback_query_id: str,
        text: str = None,
        show_alert: bool = False,
        url: str = None,
        cache_time: int = None
    ) -> Dict:
        """Answer callback query from inline buttons"""
        url = f"{self.base_url}/answerCallbackQuery"
        payload = {
            'callback_query_id': callback_query_id
        }
        
        if text:
            payload['text'] = text
        if show_alert:
            payload['show_alert'] = show_alert
        if url:
            payload['url'] = url
        if cache_time:
            payload['cache_time'] = cache_time
        
        response = requests.post(url, json=payload)
        return response.json()
    
    # 👤 USER SESSION MANAGEMENT
    
    def set_user_data(self, user_id: int, key: str, value: Any):
        """Store user-specific data"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id][key] = value
    
    def get_user_data(self, user_id: int, key: str, default: Any = None) -> Any:
        """Retrieve user-specific data"""
        return self.user_sessions.get(user_id, {}).get(key, default)
    
    def clear_user_data(self, user_id: int, key: str = None):
        """Clear user data"""
        if key:
            if user_id in self.user_sessions and key in self.user_sessions[user_id]:
                del self.user_sessions[user_id][key]
        else:
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
    
    # 📊 UTILITY METHODS
    
    def get_chat(self, chat_id: int) -> Dict:
        """Get chat information"""
        url = f"{self.base_url}/getChat"
        payload = {'chat_id': chat_id}
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def get_me(self) -> Dict:
        """Get bot information"""
        url = f"{self.base_url}/getMe"
        response = requests.post(url)
        return response.json()
    
    def forward_message(
        self,
        chat_id: int,
        from_chat_id: int,
        message_id: int
    ) -> Dict:
        """Forward a message"""
        url = f"{self.base_url}/forwardMessage"
        payload = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id
        }
        
        response = requests.post(url, json=payload)
        return response.json()

# Global bot manager instance
bot_manager = AdvancedBotManager()
