from flask import Flask, request, jsonify
import requests
import logging
import os
import importlib
import sys
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase Configuration
SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

# Global storage
user_sessions = {}
bot_data = {}
command_handlers = {}
next_command_handlers = {}

class Bot:
    @staticmethod
    def runCommand(command_name, user_info=None, chat_id=None, message_text=None):
        """Run a specific command immediately - continues to next command"""
        try:
            if command_name.startswith('/'):
                command_name = command_name[1:]  # Remove leading slash
            
            if f"/{command_name}" in command_handlers:
                handler = command_handlers[f"/{command_name}"]
                return handler(user_info, chat_id, message_text or "")
            else:
                return f"❌ Command '{command_name}' not found"
        except Exception as e:
            logger.error(f"Error running command {command_name}: {e}")
            return f"❌ Error executing command: {str(e)}"

    @staticmethod
    def handleNextCommand(command_name, user_info, chat_id):
        """Set up next command handler for user response - waits for input"""
        user_id = user_info.get('id')
        
        if command_name.startswith('/'):
            command_name = command_name[1:]  # Remove leading slash
            
        next_command_handlers[user_id] = {
            'command': command_name,
            'timestamp': datetime.now().isoformat(),
            'user_info': user_info,
            'chat_id': chat_id
        }
        return f"🔄 Waiting for your input for command: {command_name}..."

class User:
    @staticmethod
    def save_data(user_id, variable, value, user_info=None):
        """Save data for specific user"""
        try:
            # Prepare user data for tgbot_users table
            user_data = {
                "user_id": user_id,
                "updated_at": datetime.now().isoformat()
            }
            
            # Add optional user info if provided
            if user_info:
                user_data["username"] = user_info.get('username', '')
                user_data["first_name"] = user_info.get('first_name', '')
            
            # First, ensure user exists in tgbot_users
            user_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/tgbot_users",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                },
                json=user_data
            )
            
            # Now save/update data in tgbot_data
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/tgbot_data",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json", 
                    "Prefer": "resolution=merge-duplicates"
                },
                json={
                    "user_id": user_id,
                    "variable": variable,
                    "value": value,
                    "updated_at": datetime.now().isoformat()
                }
            )
            
            # Update local cache
            if user_id not in user_sessions:
                user_sessions[user_id] = {}
            user_sessions[user_id][variable] = value
            
            # Log the response for debugging
            print(f"🔍 [SAVE_DATA] User: {user_id}, Variable: {variable}, Status: {response.status_code}")
            
            if response.status_code in [200, 201, 204]:
                return "✅ Data saved successfully"
            else:
                return f"⚠️ Save completed but API returned: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return f"❌ Error: {str(e)}"

    @staticmethod
    def get_data(user_id, variable):
        """Get data for specific user"""
        try:
            # Check local cache first
            if user_id in user_sessions and variable in user_sessions[user_id]:
                return user_sessions[user_id][variable]
            
            # Fetch from Supabase
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/tgbot_data?user_id=eq.{user_id}&variable=eq.{variable}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            
            print(f"🔍 [GET_DATA] User: {user_id}, Variable: {variable}, Status: {response.status_code}")
            
            if response.status_code == 200 and response.json():
                value = response.json()[0].get('value')
                # Update local cache
                if user_id not in user_sessions:
                    user_sessions[user_id] = {}
                user_sessions[user_id][variable] = value
                return value
            return None
            
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None

def auto_discover_handlers():
    """Automatically discover all handler modules - filename as command"""
    handlers = {}
    
    try:
        handlers_dir = 'handlers'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        handlers_path = os.path.join(current_dir, handlers_dir)
        
        logger.info(f"🔍 Looking for handlers in: {handlers_path}")
        
        if os.path.exists(handlers_path):
            for filename in os.listdir(handlers_path):
                if filename.endswith('.py') and filename != '__init__.py':
                    command_name = filename[:-3]  # Remove .py
                    
                    logger.info(f"📁 Found handler file: {filename} -> /{command_name}")
                    
                    try:
                        # Use importlib to import module
                        spec = importlib.util.spec_from_file_location(
                            command_name, 
                            os.path.join(handlers_path, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Use the main function (handle function)
                        if hasattr(module, 'handle'):
                            handlers[f"/{command_name}"] = module.handle
                            logger.info(f"✅ Auto-loaded command: /{command_name}")
                        else:
                            logger.warning(f"⚠️ 'handle' function not found in {filename}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error loading handler {command_name}: {e}")
        else:
            logger.error(f"❌ Handlers directory not found: {handlers_path}")
    
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

# Initialize command handlers on startup
command_handlers = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(command_handlers)}")
logger.info(f"📋 Available commands: {list(command_handlers.keys())}")

@app.route('/', methods=['GET', 'POST', 'HEAD'])
def handle_request():
    try:
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if request.method == 'HEAD':
            return '', 200
            
        if not token:
            return jsonify({
                'error': 'Token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN to URL or set BOT_TOKEN environment variable'
            }), 400

        if request.method == 'GET':
            return jsonify({
                'status': '✅ Bot is running with FILE-BASED COMMANDS',
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
                
                logger.info(f"📩 Message from {user_info.get('first_name')}: {message_text}")
                
                # Check for next command handler first (waits for user input)
                if user_id in next_command_handlers:
                    next_command_data = next_command_handlers.pop(user_id)
                    command_name = next_command_data['command']
                    
                    if f"/{command_name}" in command_handlers:
                        response_text = command_handlers[f"/{command_name}"](
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
                available_commands = "\n".join([f"• <b>{cmd}</b>" for cmd in command_handlers.keys()])
                if available_commands:
                    response_text = f"""
❌ <b>Unknown Command:</b> <b>{message_text}</b>

📋 <b>Available Commands:</b>
{available_commands}

💡 <b>Help:</b> <b>/help</b>
"""
                else:
                    response_text = "❌ <b>No commands loaded!</b> Check server logs."
                    
                return jsonify(send_telegram_message(chat_id, response_text))
            
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'❌ Error: {e}')
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
    logger.info(f"🚀 Starting bot on port {port} with {len(command_handlers)} commands")
    app.run(host='0.0.0.0', port=port, debug=False)