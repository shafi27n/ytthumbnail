from flask import Flask, request, jsonify
import requests
import logging
import importlib
import pkgutil
import time
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase Configuration
SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXwo'

# Global storage
user_sessions = {}
bot_data = {}
command_handlers = {}
next_command_handlers = {}

class Bot:
    @staticmethod
    def runCommand(command_name, user_info=None, chat_id=None, message_text=None):
        """Run a specific command immediately"""
        try:
            if command_name in command_handlers:
                return command_handlers[command_name](user_info, chat_id, message_text)
            else:
                return f"❌ Command '{command_name}' not found"
        except Exception as e:
            logger.error(f"Error running command {command_name}: {e}")
            return f"❌ Error executing command: {str(e)}"

    @staticmethod
    def handleNextCommand(command_name, user_info, chat_id):
        """Set up next command handler for user response"""
        user_id = user_info.get('id')
        next_command_handlers[user_id] = {
            'command': command_name,
            'timestamp': time.time(),
            'user_info': user_info,
            'chat_id': chat_id
        }
        return "🔄 Waiting for your response..."

    @staticmethod
    def save_data(variable, value):
        """Save data for all users (bot-wide)"""
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/bot_data",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json={
                    "variable": variable,
                    "value": value,
                    "created_at": datetime.now().isoformat()
                }
            )
            bot_data[variable] = value
            return f"✅ Bot data saved: {variable} = {value}"
        except Exception as e:
            logger.error(f"Error saving bot data: {e}")
            return f"❌ Error saving bot data: {str(e)}"

class User:
    @staticmethod
    def save_data(user_id, variable, value):
        """Save data for specific user"""
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_data",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json={
                    "user_id": user_id,
                    "variable": variable,
                    "value": value,
                    "created_at": datetime.now().isoformat()
                }
            )
            if user_id not in user_sessions:
                user_sessions[user_id] = {}
            user_sessions[user_id][variable] = value
            return f"✅ User data saved: {variable} = {value}"
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return f"❌ Error saving user data: {str(e)}"

    @staticmethod
    def get_data(user_id, variable):
        """Get data for specific user"""
        try:
            if user_id in user_sessions and variable in user_sessions[user_id]:
                return user_sessions[user_id][variable]
            
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/user_data?user_id=eq.{user_id}&variable=eq.{variable}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            if response.status_code == 200 and response.json():
                return response.json()[0].get('value')
            return None
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None

def auto_discover_handlers():
    """Automatically discover all handler modules"""
    handlers = {}
    
    try:
        handlers_package = importlib.import_module('bot.handlers')
        
        for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
            if module_name != '__init__':
                try:
                    module = importlib.import_module(f'bot.handlers.{module_name}')
                    
                    # Handle multiple commands from filename (name1|name2|name3.py)
                    command_names = module_name.split('|')
                    
                    for command_name in command_names:
                        function_name = f"handle_{command_name}"
                        if hasattr(module, function_name):
                            handlers[f"/{command_name}"] = getattr(module, function_name)
                            logger.info(f"✅ Auto-loaded command: /{command_name}")
                        else:
                            logger.warning(f"⚠️ Function {function_name} not found in {module_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error loading handler {module_name}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error discovering handlers: {e}")
    
    return handlers

def send_telegram_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    """Send message with various options"""
    message_data = {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    if reply_markup:
        message_data['reply_markup'] = reply_markup
        
    return message_data

def create_keyboard(buttons, resize_keyboard=True, one_time_keyboard=False):
    """Create reply keyboard markup"""
    return {
        'keyboard': buttons,
        'resize_keyboard': resize_keyboard,
        'one_time_keyboard': one_time_keyboard
    }

def create_inline_keyboard(buttons):
    """Create inline keyboard markup"""
    return {
        'inline_keyboard': buttons
    }

# Initialize command handlers
command_handlers = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(command_handlers)}")

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    try:
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if not token:
            return jsonify({
                'error': 'Token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN to URL or set BOT_TOKEN environment variable'
            }), 400

        if request.method == 'GET':
            return jsonify({
                'status': 'Bot is running with ADVANCED AUTO-MODULAR architecture',
                'available_commands': list(command_handlers.keys()),
                'total_commands': len(command_handlers),
                'active_sessions': len(next_command_handlers),
                'timestamp': datetime.now().isoformat()
            })

        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                message_text = update['message'].get('text', '').strip()
                user_info = update['message'].get('from', {})
                user_id = user_info.get('id')
                
                logger.info(f"Message from {user_info.get('first_name')}: {message_text}")
                
                # Check for next command handler first
                if user_id in next_command_handlers:
                    next_command_data = next_command_handlers.pop(user_id)
                    command_name = next_command_data['command']
                    
                    if command_name in command_handlers:
                        response_text = command_handlers[command_name](
                            next_command_data['user_info'], 
                            next_command_data['chat_id'], 
                            message_text
                        )
                        return jsonify(send_telegram_message(chat_id, response_text))
                
                # Handle regular commands
                for command, handler in command_handlers.items():
                    if message_text.startswith(command):
                        try:
                            response_text = handler(user_info, chat_id, message_text)
                            return jsonify(send_telegram_message(chat_id, response_text))
                        except Exception as e:
                            error_msg = f"❌ Error executing command: {str(e)}"
                            logger.error(f"Command error: {e}")
                            return jsonify(send_telegram_message(chat_id, error_msg))
                
                # Default response for unknown commands
                available_commands = "\n".join([f"• <code>{cmd}</code>" for cmd in command_handlers.keys()])
                return jsonify(send_telegram_message(
                    chat_id, 
                    f"❌ <b>Unknown Command:</b> <code>{message_text}</code>\n\n"
                    f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
                    f"💡 <b>Help:</b> <code>/help</code>"
                ))
            
            # Handle callback queries (inline buttons)
            elif 'callback_query' in update:
                callback_query = update['callback_query']
                chat_id = callback_query['message']['chat']['id']
                user_info = callback_query['from']
                data = callback_query['data']
                
                # Answer callback query first
                requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", 
                             json={'callback_query_id': callback_query['id']})
                
                # Handle callback data
                response_text = f"🔄 Callback received: {data}"
                return jsonify(send_telegram_message(chat_id, response_text))
            
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'Error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(command_handlers),
        'commands': list(command_handlers.keys()),
        'active_sessions': len(next_command_handlers),
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
