from flask import Flask, request, jsonify
import requests
import json
import os
import logging
import importlib
import pkgutil
from datetime import datetime
from supabase_client import supabase
import traceback
import sys

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class TelegramBot:
    def __init__(self, token=None):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}" if token else None
        self.user_sessions = {}
        self.pending_commands = {}
        self.supabase = supabase
        self.message_logs = []
        self.error_logs = []
        self.system_logs = []
        
        # Log startup
        self.log_system("Bot instance created")
    
    def log_message(self, user_info, message_text, response_text, chat_id):
        """Log user messages and bot responses"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_info.get('id'),
            'first_name': user_info.get('first_name', 'Unknown'),
            'username': user_info.get('username', 'No username'),
            'chat_id': chat_id,
            'user_message': message_text,
            'bot_response': response_text,
            'type': 'message'
        }
        
        self.message_logs.append(log_entry)
        logger.info(f"💬 Message from {user_info.get('first_name')}: {message_text}")
        
        # Save to Supabase for persistence
        try:
            self.supabase.user_save_data(
                user_info.get('id'), 
                f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                json.dumps(log_entry)
            )
        except Exception as e:
            logger.error(f"Failed to save log to Supabase: {e}")
    
    def log_error(self, error_type, error_message, user_info=None, chat_id=None):
        """Log errors with context"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'user_info': user_info,
            'chat_id': chat_id,
            'type': 'error'
        }
        
        self.error_logs.append(log_entry)
        logger.error(f"🚨 {error_type}: {error_message}")
        
        # Save error to Supabase
        try:
            self.supabase.bot_save_data(
                f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                json.dumps(log_entry)
            )
        except Exception as e:
            logger.error(f"Failed to save error log: {e}")
    
    def log_system(self, message):
        """Log system events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': 'system'
        }
        
        self.system_logs.append(log_entry)
        logger.info(f"🔧 SYSTEM: {message}")
    
    def get_recent_logs(self, log_type='all', limit=50):
        """Get recent logs by type"""
        if log_type == 'messages':
            logs = self.message_logs[-limit:]
        elif log_type == 'errors':
            logs = self.error_logs[-limit:]
        elif log_type == 'system':
            logs = self.system_logs[-limit:]
        else:
            # Combine all logs
            all_logs = self.message_logs + self.error_logs + self.system_logs
            logs = sorted(all_logs, key=lambda x: x['timestamp'])[-limit:]
        
        return logs
    
    def get_user_logs(self, user_id, limit=20):
        """Get logs for specific user"""
        user_logs = [
            log for log in self.message_logs 
            if log.get('user_id') == user_id
        ][-limit:]
        return user_logs
    
    def get_stats(self):
        """Get bot statistics"""
        return {
            'total_messages': len(self.message_logs),
            'total_errors': len(self.error_logs),
            'total_system_logs': len(self.system_logs),
            'active_users': len(set(log.get('user_id') for log in self.message_logs)),
            'user_sessions': len(self.user_sessions),
            'pending_commands': len(self.pending_commands)
        }

    def set_token(self, token):
        """Set bot token dynamically"""
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.log_system(f"Bot token set: {token[:10]}...")
    
    def run_command(self, command_name, user_info, chat_id, message_text, **kwargs):
        """Execute specific command by name"""
        try:
            # Remove slash from command name
            clean_name = command_name.replace('/', '')
            
            # Import handler module
            module = importlib.import_module(f'handlers.{clean_name}')
            
            # Get handler function
            handler_func = getattr(module, f'handle_{clean_name}')
            
            # Execute command
            self.log_system(f"Executing command: {command_name} for user {user_info.get('id')}")
            response = handler_func(user_info, chat_id, message_text, bot=self, **kwargs)
            
            # Log successful command execution
            self.log_message(user_info, message_text, response, chat_id)
            return response
            
        except Exception as e:
            error_msg = f"Command error {command_name}: {str(e)}"
            self.log_error("COMMAND_EXECUTION", error_msg, user_info, chat_id)
            return self.get_error_message("command_execution")
    
    def handle_next_command(self, chat_id, next_command, user_info=None):
        """Wait for user's next response"""
        self.pending_commands[chat_id] = {
            'command': next_command,
            'user_info': user_info,
            'timestamp': datetime.now()
        }
        self.log_system(f"Set pending command {next_command} for chat {chat_id}")
    
    def process_pending_command(self, chat_id, message_text, user_info):
        """Process pending command response"""
        if chat_id in self.pending_commands:
            pending = self.pending_commands.pop(chat_id)
            command = pending['command']
            self.log_system(f"Processing pending command {command} for chat {chat_id}")
            return self.run_command(command, user_info, chat_id, message_text, is_pending=True)
        return None
    
    def get_error_message(self, error_type):
        """Get user-friendly error messages"""
        error_messages = {
            "command_execution": """
❌ <b>Command Execution Error</b>

🚨 <b>What happened:</b>
There was an error executing your command.

💡 <b>Possible solutions:</b>
• Try again in a few moments
• Use <code>/help</code> for available commands
• Contact admin if problem persists

🔧 <b>Technical Info:</b>
The error has been logged for investigation.
""",
            "handler_not_found": """
❌ <b>Handler Not Found</b>

🚨 <b>What happened:</b>
The command handler is not available.

💡 <b>What to do:</b>
• Check available commands with <code>/help</code>
• The command might be under maintenance
• Try again later
""",
            "general_error": """
❌ <b>Something Went Wrong</b>

🚨 <b>Don't worry!</b>
This is a temporary issue.

💡 <b>Quick fixes:</b>
• Try your command again
• Use <code>/start</code> to restart
• Check <code>/help</code> for commands

🛠️ <b>Our team has been notified</b>
"""
        }
        return error_messages.get(error_type, error_messages["general_error"])
    
    # 🔧 BASIC TELEGRAM API METHODS
    
    def send_message(self, chat_id, text, parse_mode='HTML', reply_markup=None):
        """Send text message with error handling"""
        if not self.token:
            return {'ok': False, 'error': 'Token not set'}
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            self.log_error("SEND_MESSAGE", str(e))
            return {'ok': False, 'error': str(e)}
    
    def send_photo(self, chat_id, photo_url, caption=None, parse_mode='HTML'):
        """Send photo from URL"""
        if not self.token:
            return {'ok': False, 'error': 'Token not set'}
        
        url = f"{self.base_url}/sendPhoto"
        payload = {
            'chat_id': chat_id,
            'photo': photo_url
        }
        
        if caption:
            payload['caption'] = caption
            payload['parse_mode'] = parse_mode
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            self.log_error("SEND_PHOTO", str(e))
            return {'ok': False, 'error': str(e)}
    
    def edit_message(self, chat_id, message_id, text, parse_mode='HTML', reply_markup=None):
        """Edit existing message"""
        if not self.token:
            return {'ok': False, 'error': 'Token not set'}
        
        url = f"{self.base_url}/editMessageText"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            self.log_error("EDIT_MESSAGE", str(e))
            return {'ok': False, 'error': str(e)}
    
    def delete_message(self, chat_id, message_id):
        """Delete message"""
        if not self.token:
            return {'ok': False, 'error': 'Token not set'}
        
        url = f"{self.base_url}/deleteMessage"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            self.log_error("DELETE_MESSAGE", str(e))
            return {'ok': False, 'error': str(e)}
    
    # 🎛️ KEYBOARD METHODS
    
    def create_inline_keyboard(self, buttons):
        """Create inline keyboard markup"""
        return {'inline_keyboard': buttons}
    
    def create_reply_keyboard(self, buttons, resize=True, one_time=False):
        """Create reply keyboard markup"""
        return {
            'keyboard': buttons,
            'resize_keyboard': resize,
            'one_time_keyboard': one_time
        }
    
    def remove_keyboard(self):
        """Remove reply keyboard"""
        return {'remove_keyboard': True}
    
    def create_button(self, text, url=None, callback_data=None):
        """Create inline button"""
        button = {'text': text}
        
        if url:
            button['url'] = url
        elif callback_data:
            button['callback_data'] = callback_data
        
        return button
    
    # 🌐 HTTP REQUEST METHODS
    
    def http_get(self, url, headers=None, params=None):
        """Perform HTTP GET request"""
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            return {
                'success': True,
                'status_code': response.status_code,
                'content': response.text,
                'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
            }
        except Exception as e:
            self.log_error("HTTP_GET", str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    def http_post(self, url, data=None, json_data=None, headers=None):
        """Perform HTTP POST request"""
        try:
            response = requests.post(url, data=data, json=json_data, headers=headers, timeout=10)
            return {
                'success': True,
                'status_code': response.status_code,
                'content': response.text,
                'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
            }
        except Exception as e:
            self.log_error("HTTP_POST", str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    # 💾 SUPABASE DATA METHODS
    
    def user_save_data(self, user_id, variable, value):
        """Save user data to Supabase"""
        result = self.supabase.user_save_data(user_id, variable, value)
        if result:
            self.log_system(f"User data saved: {user_id} - {variable} = {value}")
        else:
            self.log_error("USER_SAVE_DATA", f"Failed to save data for user {user_id}")
        return result
    
    def user_get_data(self, user_id, variable):
        """Get user data from Supabase"""
        return self.supabase.user_get_data(user_id, variable)
    
    def user_get_all_data(self, user_id):
        """Get all data for a user"""
        return self.supabase.user_get_all_data(user_id)
    
    def bot_save_data(self, variable, value):
        """Save bot data to Supabase"""
        result = self.supabase.bot_save_data(variable, value)
        if result:
            self.log_system(f"Bot data saved: {variable} = {value}")
        else:
            self.log_error("BOT_SAVE_DATA", f"Failed to save bot data: {variable}")
        return result
    
    def bot_get_data(self, variable):
        """Get bot data from Supabase"""
        return self.supabase.bot_get_data(variable)
    
    def delete_user_data(self, user_id, variable=None):
        """Delete user data"""
        result = self.supabase.delete_user_data(user_id, variable)
        if result:
            self.log_system(f"User data deleted: {user_id} - {variable}")
        else:
            self.log_error("DELETE_USER_DATA", f"Failed to delete data for user {user_id}")
        return result

# Create bot instance
bot = TelegramBot()

def auto_discover_handlers():
    """Automatically discover all command handlers with error handling"""
    handlers = {}
    
    try:
        # Import handlers package
        handlers_package = importlib.import_module('handlers')
        
        # Discover all modules in handlers package
        for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
            if module_name != '__init__' and not module_name.startswith('_'):
                try:
                    module = importlib.import_module(f'handlers.{module_name}')
                    
                    # Look for handle_ functions
                    for attr_name in dir(module):
                        if attr_name.startswith('handle_'):
                            command_name = f"/{attr_name.replace('handle_', '')}"
                            handlers[command_name] = getattr(module, attr_name)
                            logger.info(f"✅ Loaded command: {command_name}")
                            
                except Exception as e:
                    logger.error(f"❌ Error loading {module_name}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Handler discovery error: {e}")
        # Don't crash the app, just log the error
    
    return handlers

# Auto-load handlers on startup
COMMAND_HANDLERS = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(COMMAND_HANDLERS)}")

@app.route('/', methods=['GET', 'POST'])
def handle_webhook():
    """Main webhook handler with comprehensive error handling"""
    try:
        # Get token from URL or environment
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if not token:
            return jsonify({
                'error': 'Bot token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN or set BOT_TOKEN environment variable'
            }), 400
        
        # Set bot token
        bot.set_token(token)
        
        if request.method == 'GET':
            stats = bot.get_stats()
            return jsonify({
                'status': '🚀 Telegram Bot is Running!',
                'commands': list(COMMAND_HANDLERS.keys()),
                'total_commands': len(COMMAND_HANDLERS),
                'supabase_connected': True,
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            })
        
        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            # Handle message
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                message_text = message.get('text', '').strip()
                user_info = message.get('from', {})
                
                logger.info(f"📩 Message from {user_info.get('first_name')}: {message_text}")
                
                # Check for pending commands first
                pending_response = bot.process_pending_command(chat_id, message_text, user_info)
                if pending_response:
                    return jsonify(bot.send_message(chat_id, pending_response))
                
                # Execute command handlers
                for command, handler in COMMAND_HANDLERS.items():
                    if message_text.startswith(command):
                        response_text = handler(user_info, chat_id, message_text, bot=bot)
                        return jsonify(bot.send_message(chat_id, response_text))
                
                # Unknown command
                if COMMAND_HANDLERS:
                    commands_list = "\n".join([f"• <code>{cmd}</code>" for cmd in COMMAND_HANDLERS.keys()])
                    error_msg = f"""
❌ <b>Unknown Command</b>

🚫 <b>Command:</b> <code>{message_text}</code>

📋 <b>Available Commands:</b>
{commands_list}

💡 <b>Need help?</b> Try <code>/help</code>
                    """
                else:
                    error_msg = bot.get_error_message("handler_not_found")
                
                return jsonify(bot.send_message(chat_id, error_msg))
            
            return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"🚨 Webhook error: {e}")
        bot.log_error("WEBHOOK_ERROR", str(e))
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = bot.get_stats()
    return jsonify({
        'status': 'healthy',
        'commands_loaded': len(COMMAND_HANDLERS),
        'statistics': stats,
        'supabase_connected': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get bot logs via web interface"""
    try:
        log_type = request.args.get('type', 'all')
        limit = int(request.args.get('limit', 50))
        user_id = request.args.get('user_id')
        
        if user_id:
            logs = bot.get_user_logs(int(user_id), limit)
        else:
            logs = bot.get_recent_logs(log_type, limit)
        
        stats = bot.get_stats()
        
        return jsonify({
            'status': 'success',
            'log_type': log_type,
            'limit': limit,
            'user_id': user_id,
            'statistics': stats,
            'logs': logs,
            'total_logs': len(logs),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Logs endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs/clear', methods=['POST'])
def clear_logs():
    """Clear in-memory logs (doesn't affect Supabase)"""
    try:
        bot.message_logs.clear()
        bot.error_logs.clear()
        bot.system_logs.clear()
        
        bot.log_system("All in-memory logs cleared via API")
        
        return jsonify({
            'status': 'success',
            'message': 'All in-memory logs cleared',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Clear logs error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug information endpoint"""
    stats = bot.get_stats()
    
    return jsonify({
        'command_handlers': list(COMMAND_HANDLERS.keys()),
        'user_sessions': bot.user_sessions,
        'pending_commands': bot.pending_commands,
        'statistics': stats,
        'memory_logs_count': {
            'messages': len(bot.message_logs),
            'errors': len(bot.error_logs),
            'system': len(bot.system_logs)
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting bot server on port {port}")
    logger.info(f"📦 Loaded {len(COMMAND_HANDLERS)} command handlers")
    
    # Log startup information
    bot.log_system("Bot server starting up")
    bot.log_system(f"Port: {port}")
    bot.log_system(f"Command handlers: {len(COMMAND_HANDLERS)}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
