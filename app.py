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
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXwo'

# Global storage
user_sessions = {}
bot_data = {}
command_handlers = {}
next_command_handlers = {}
command_queue = {}
module_cache = {}  # Cache loaded modules

class Bot:
    @staticmethod
    def runCommand(command_name, user_info=None, chat_id=None, message_text=None):
        """Run a specific command immediately - continues execution"""
        try:
            logger.info(f"🚀 Executing immediate command: {command_name}")
            
            if command_name in command_handlers:
                handler_func = command_handlers[command_name]
                if callable(handler_func):
                    result = handler_func(user_info, chat_id, message_text)
                else:
                    # If it's a module, execute the main function
                    result = handler_func['execute'](user_info, chat_id, message_text, command_name)
                logger.info(f"✅ Command {command_name} executed successfully")
                return result
            else:
                error_msg = f"❌ Command '{command_name}' not found"
                logger.warning(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"❌ Error executing command {command_name}: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def handleNextCommand(command_name, user_info, chat_id, current_response=""):
        """Set up next command handler for user response - pauses execution"""
        user_id = user_info.get('id')
        
        logger.info(f"⏳ Setting up next command: {command_name} for user {user_id}")
        
        next_command_handlers[user_id] = {
            'command': command_name,
            'timestamp': datetime.now().isoformat(),
            'user_info': user_info,
            'chat_id': chat_id
        }
        
        # Return current response + waiting message
        if current_response:
            return current_response + f"\n\n🔄 Waiting for your input to continue with <b>/{command_name}</b>..."
        else:
            return f"🔄 Waiting for your input to continue with <b>/{command_name}</b>..."

    @staticmethod
    def queueCommand(command_name, user_info, chat_id):
        """Queue a command to run after current execution"""
        user_id = user_info.get('id')
        
        if user_id not in command_queue:
            command_queue[user_id] = []
        
        command_queue[user_id].append({
            'command': command_name,
            'user_info': user_info,
            'chat_id': chat_id,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"📥 Queued command: {command_name} for user {user_id}")

    @staticmethod
    def processQueuedCommands(user_id, chat_id):
        """Process all queued commands for a user"""
        if user_id in command_queue and command_queue[user_id]:
            results = []
            for queued in command_queue[user_id]:
                try:
                    result = Bot.runCommand(
                        queued['command'],
                        queued['user_info'],
                        queued['chat_id']
                    )
                    results.append(result)
                except Exception as e:
                    results.append(f"❌ Error in queued command {queued['command']}: {str(e)}")
            
            # Clear the queue
            command_queue[user_id] = []
            
            return "\n\n".join(results)
        return None

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
        """Save data for specific user using new table structure"""
        try:
            # First, ensure user exists in tgbot_users
            user_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/tgbot_users",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                },
                json={
                    "user_id": user_id,
                    "updated_at": datetime.now().isoformat()
                }
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
            
            if response.status_code in [200, 201, 204]:
                # Update local cache
                if user_id not in user_sessions:
                    user_sessions[user_id] = {}
                user_sessions[user_id][variable] = value
                return f"✅ Data saved: {variable}"
            else:
                return f"❌ Save failed: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return f"❌ Error: {str(e)}"

    @staticmethod
    def get_data(user_id, variable):
        """Get data for specific user from new tables"""
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

def execute_module_function(module, user_info, chat_id, message_text, command_name):
    """Execute the main function from a module"""
    try:
        # Try to find and execute main function
        if hasattr(module, 'main'):
            return module.main(user_info, chat_id, message_text, command_name)
        elif hasattr(module, 'execute'):
            return module.execute(user_info, chat_id, message_text, command_name)
        else:
            # If no main function, try to execute the module directly
            return f"❌ Module {module.__name__} has no executable function"
    except Exception as e:
        return f"❌ Error executing module: {str(e)}"

def auto_discover_handlers():
    """Automatically discover all handler modules - NEW SYSTEM"""
    handlers = {}
    
    try:
        handlers_dir = 'handlers'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        handlers_path = os.path.join(current_dir, handlers_dir)
        
        logger.info(f"🔍 Looking for handlers in: {handlers_path}")
        
        if os.path.exists(handlers_path):
            for filename in os.listdir(handlers_path):
                if filename.endswith('.py') and filename != '__init__.py':
                    module_name = filename[:-3]  # Remove .py
                    
                    logger.info(f"📁 Found handler file: {filename}")
                    
                    try:
                        # Use importlib to import module
                        spec = importlib.util.spec_from_file_location(
                            module_name, 
                            os.path.join(handlers_path, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Cache the module
                        module_cache[module_name] = module
                        
                        # Handle multiple commands from filename (name1,name2,name3.py)
                        command_names = module_name.split(',')
                        
                        for command_name in command_names:
                            # Register the module for this command
                            handlers[f"/{command_name}"] = {
                                'module': module,
                                'execute': lambda u, c, m, cmd=command_name: execute_module_function(module, u, c, m, cmd)
                            }
                            logger.info(f"✅ Auto-loaded command: /{command_name} from module {module_name}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error loading handler {module_name}: {e}")
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
        # Get token from URL parameter or environment variable
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
                'status': '✅ Bot is running with MODULE-BASED COMMAND SYSTEM',
                'available_commands': list(command_handlers.keys()),
                'total_commands': len(command_handlers),
                'active_sessions': len(next_command_handlers),
                'queued_commands': sum(len(q) for q in command_queue.values()),
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
                
                # Check for next command handler first (paused execution)
                if user_id in next_command_handlers:
                    next_command_data = next_command_handlers.pop(user_id)
                    command_name = next_command_data['command']
                    
                    if command_name in command_handlers:
                        logger.info(f"🔄 Resuming paused command: {command_name}")
                        handler_data = command_handlers[command_name]
                        response_text = handler_data['execute'](
                            next_command_data['user_info'], 
                            next_command_data['chat_id'], 
                            message_text,
                            command_name
                        )
                        
                        # Process any queued commands after resuming
                        queued_result = Bot.processQueuedCommands(user_id, chat_id)
                        if queued_result:
                            response_text += f"\n\n{queued_result}"
                            
                        return jsonify(send_telegram_message(chat_id, response_text))
                
                # Process queued commands if any
                queued_result = Bot.processQueuedCommands(user_id, chat_id)
                if queued_result:
                    return jsonify(send_telegram_message(chat_id, queued_result))
                
                # Handle regular commands
                for command, handler_data in command_handlers.items():
                    if message_text.startswith(command):
                        try:
                            response_text = handler_data['execute'](user_info, chat_id, message_text, command)
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
        'queued_commands': sum(len(q) for q in command_queue.values()),
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting bot on port {port} with {len(command_handlers)} commands")
    app.run(host='0.0.0.0', port=port, debug=False)