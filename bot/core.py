import os
import logging
from supabase import create_client, Client
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import requests
import json
from typing import Dict, Any, List, Optional, Callable

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Supabase Configuration
SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

class BotDatabase:
    """Supabase database operations for bot and user data"""
    
    def __init__(self):
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Supabase connected successfully")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            self.supabase = None
    
    def save_bot_data(self, variable: str, value: Any) -> bool:
        """Save data for all users (bot-level data)"""
        try:
            if not self.supabase:
                return False
            
            data = {
                'variable': variable,
                'value': value,
                'type': 'bot_data',
                'updated_at': 'now()'
            }
            
            # Check if variable exists
            existing = self.supabase.table('bot_data')\
                .select('*')\
                .eq('variable', variable)\
                .execute()
            
            if existing.data:
                # Update existing
                self.supabase.table('bot_data')\
                    .update({'value': value, 'updated_at': 'now()'})\
                    .eq('variable', variable)\
                    .execute()
            else:
                # Insert new
                self.supabase.table('bot_data').insert(data).execute()
            
            logger.info(f"✅ Bot data saved: {variable} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving bot data: {e}")
            return False
    
    def get_bot_data(self, variable: str, default: Any = None) -> Any:
        """Get bot-level data"""
        try:
            if not self.supabase:
                return default
            
            result = self.supabase.table('bot_data')\
                .select('value')\
                .eq('variable', variable)\
                .execute()
            
            if result.data:
                return result.data[0]['value']
            return default
            
        except Exception as e:
            logger.error(f"❌ Error getting bot data: {e}")
            return default
    
    def save_user_data(self, user_id: int, variable: str, value: Any) -> bool:
        """Save data for specific user"""
        try:
            if not self.supabase:
                return False
            
            data = {
                'user_id': user_id,
                'variable': variable,
                'value': value,
                'updated_at': 'now()'
            }
            
            # Check if exists
            existing = self.supabase.table('user_data')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('variable', variable)\
                .execute()
            
            if existing.data:
                # Update
                self.supabase.table('user_data')\
                    .update({'value': value, 'updated_at': 'now()'})\
                    .eq('user_id', user_id)\
                    .eq('variable', variable)\
                    .execute()
            else:
                # Insert
                self.supabase.table('user_data').insert(data).execute()
            
            logger.info(f"✅ User data saved: user_{user_id}.{variable} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: int, variable: str, default: Any = None) -> Any:
        """Get user-specific data"""
        try:
            if not self.supabase:
                return default
            
            result = self.supabase.table('user_data')\
                .select('value')\
                .eq('user_id', user_id)\
                .eq('variable', variable)\
                .execute()
            
            if result.data:
                return result.data[0]['value']
            return default
            
        except Exception as e:
            logger.error(f"❌ Error getting user data: {e}")
            return default
    
    def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get all user data as context"""
        try:
            if not self.supabase:
                return {}
            
            result = self.supabase.table('user_data')\
                .select('variable, value')\
                .eq('user_id', user_id)\
                .execute()
            
            context = {}
            for item in result.data:
                context[item['variable']] = item['value']
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Error getting user context: {e}")
            return {}

class BotCore:
    """Core bot functionality with advanced features"""
    
    def __init__(self):
        self.db = BotDatabase()
        self.waiting_commands: Dict[int, str] = {}  # user_id -> command
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
    
    async def run_command(self, command_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Run a specific command by name"""
        try:
            # Import and execute command
            module_name = f"bot.handlers.{command_name}"
            module = __import__(module_name, fromlist=[''])
            
            handler_func = getattr(module, f"handle_{command_name}", None)
            if handler_func:
                await handler_func(update, context, self)
                return True
            else:
                await self.send_error_message(update, f"Command handler not found: {command_name}")
                return False
                
        except Exception as e:
            error_msg = f"Error running command {command_name}: {str(e)}"
            logger.error(error_msg)
            await self.send_error_message(update, error_msg)
            return False
    
    async def handle_next_command(self, command_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Wait for user response and then run command"""
        try:
            user_id = update.effective_user.id
            self.waiting_commands[user_id] = command_name
            
            # Save in user session
            self.user_sessions[user_id] = {
                'waiting_for_command': command_name,
                'original_message': update.message.text if update.message else ""
            }
            
            # Also save to database for persistence
            self.db.save_user_data(user_id, 'waiting_command', command_name)
            
            await update.message.reply_text(
                f"🔄 Please provide your response for the command: `{command_name}`\n\n"
                "I'm waiting for your input...",
                parse_mode='Markdown'
            )
            return True
            
        except Exception as e:
            error_msg = f"Error setting up next command: {str(e)}"
            logger.error(error_msg)
            await self.send_error_message(update, error_msg)
            return False
    
    async def process_waiting_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Process user response for waiting command"""
        try:
            user_id = update.effective_user.id
            
            # Get waiting command from memory or database
            waiting_command = self.waiting_commands.get(user_id)
            if not waiting_command:
                waiting_command = self.db.get_user_data(user_id, 'waiting_command')
            
            if waiting_command:
                # Clear waiting state
                if user_id in self.waiting_commands:
                    del self.waiting_commands[user_id]
                self.db.save_user_data(user_id, 'waiting_command', None)
                
                # Store user response in context
                user_response = update.message.text if update.message else ""
                context.user_data['user_response'] = user_response
                
                # Run the waiting command
                return await self.run_command(waiting_command, update, context)
            else:
                return False
                
        except Exception as e:
            error_msg = f"Error processing waiting command: {str(e)}"
            logger.error(error_msg)
            await self.send_error_message(update, error_msg)
            return False
    
    async def send_error_message(self, update: Update, error_message: str):
        """Send error message to user"""
        try:
            if update.message:
                await update.message.reply_text(
                    f"❌ *Error:*\n`{error_message}`\n\n"
                    "Please try again or contact support.",
                    parse_mode='Markdown'
                )
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    f"❌ *Error:*\n`{error_message}`",
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    async def send_message(self, update: Update, text: str, 
                         parse_mode: str = 'HTML', 
                         reply_markup: Any = None,
                         reply_to_message_id: int = None) -> bool:
        """Send message with various options"""
        try:
            if update.message:
                await update.message.reply_text(
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    reply_to_message_id=reply_to_message_id
                )
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def edit_message(self, update: Update, text: str, 
                         parse_mode: str = 'HTML',
                         reply_markup: Any = None) -> bool:
        """Edit existing message"""
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return False
    
    async def delete_message(self, update: Update, message_id: int = None) -> bool:
        """Delete message"""
        try:
            if message_id and update.effective_chat:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=message_id
                )
                return True
            elif update.message:
                await update.message.delete()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    async def send_photo(self, update: Update, photo_url: str, 
                       caption: str = "", parse_mode: str = 'HTML',
                       reply_markup: Any = None) -> bool:
        """Send photo"""
        try:
            if update.message:
                await update.message.reply_photo(
                    photo=photo_url,
                    caption=caption,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return False
    
    async def send_video(self, update: Update, video_url: str,
                       caption: str = "", parse_mode: str = 'HTML',
                       reply_markup: Any = None) -> bool:
        """Send video"""
        try:
            if update.message:
                await update.message.reply_video(
                    video=video_url,
                    caption=caption,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error sending video: {e}")
            return False
    
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
        """Create inline keyboard markup"""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(InlineKeyboardButton(
                    text=button['text'],
                    callback_data=button.get('callback_data'),
                    url=button.get('url')
                ))
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(keyboard)
    
    def create_reply_keyboard(self, buttons: List[List[str]], 
                            resize_keyboard: bool = True,
                            one_time_keyboard: bool = False) -> ReplyKeyboardMarkup:
        """Create reply keyboard markup"""
        keyboard = []
        for row in buttons:
            keyboard_row = [KeyboardButton(text) for text in row]
            keyboard.append(keyboard_row)
        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard
        )
    
    async def http_request(self, method: str, url: str, 
                         headers: Dict = None, 
                         data: Dict = None, 
                         json_data: Dict = None) -> Dict[str, Any]:
        """Make HTTP requests"""
        try:
            method = method.lower()
            if method == 'get':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'post':
                response = requests.post(url, headers=headers, data=data, json=json_data)
            elif method == 'put':
                response = requests.put(url, headers=headers, data=data, json=json_data)
            elif method == 'delete':
                response = requests.delete(url, headers=headers)
            else:
                return {'error': f'Unsupported HTTP method: {method}'}
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'text': response.text,
                'json': response.json() if response.headers.get('content-type') == 'application/json' else None
            }
            
        except Exception as e:
            return {'error': str(e)}

# Global bot instance
bot_core = BotCore()

# Shortcut functions for easy access
def Bot():
    return bot_core

def User(user_id: int):
    return bot_core.db