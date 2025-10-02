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
module_cache = {}

class Bot:
    @staticmethod
    def runCommand(command_name, user_info=None, chat_id=None, message_text=None):
        """Run a specific command immediately - continues execution"""
        try:
            logger.info(f"🚀 Executing immediate command: {command_name}")
            
            if command_name in command_handlers:
                handler_data = command_handlers[command_name]
                result = handler_data['execute'](user_info, chat_id, message_text, command_name)
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
            
            command_queue[user_id] = []
            return "\n\n".join(results)
        return None

def execute_module_function(module, user_info, chat_id, message_text, command_name):
    """Execute the appropriate function from a module based on command name"""
    try:
        # Try to find specific function for this command
        function_name = f"handle_{command_name}"
        if hasattr(module, function_name):
            return getattr(module, function_name)(user_info, chat_id, message_text)
        
        # Try main function
        elif hasattr(module, 'main'):
            return module.main(user_info, chat_id, message_text, command_name)
        
        # Try execute function
        elif hasattr(module, 'execute'):
            return module.execute(user_info, chat_id, message_text, command_name)
        
        else:
            # If no specific function, check for any handle_ function
            for attr_name in dir(module):
                if attr_name.startswith('handle_'):
                    func = getattr(module, attr_name)
                    if callable(func):
                        return func(user_info, chat_id, message_text)
            
            return f"❌ No executable function found for command: {command_name}"
            
    except Exception as e:
        return f"❌ Error executing command {command_name}: {str(e)}"

def auto_discover_handlers():
    """Automatically discover all handler modules - FIXED VERSION"""
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
                'status': '✅ Bot is running with FIXED COMMAND SYSTEM',
                'available_commands': list(command_handlers.keys()),
                'total_commands': len(command_handlers),
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
                
                # Check for next command handler first
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
                        return jsonify(send_telegram_message(chat_id, response_text))
                
                # Process queued commands if any
                queued_result = Bot.processQueuedCommands(user_id, chat_id)
                if queued_result:
                    return jsonify(send_telegram_message(chat_id, queued_result))
                
                # Handle regular commands
                for command, handler_data in command_handlers.items():
                    if message_text.startswith(command):
                        try:
                            response_text = handler_data['execute'](user_info, chat_id, message_text, command[1:])  # Remove leading /
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting bot on port {port} with {len(command_handlers)} commands")
    app.run(host='0.0.0.0', port=port, debug=False)