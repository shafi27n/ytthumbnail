from flask import Flask, request, jsonify
import os
import logging
import importlib
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import bot manager
try:
    from bot.core.bot_manager import bot_manager
    logger.info("✅ Bot manager imported successfully")
except ImportError as e:
    logger.error(f"❌ Bot manager import failed: {e}")
    # Fallback manager
    class SimpleManager:
        def __init__(self): 
            self.user_sessions = {}
            self.pending_responses = {}
        def set_token(self, token): 
            self.token = token
            logger.info(f"✅ Token set: {token[:10]}...")
        def send_message(self, chat_id, text, **kwargs): 
            return {'method': 'sendMessage', 'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        def handle_next_command(self, chat_id, command, user_info=None):
            self.pending_responses[chat_id] = {'expected_command': command, 'user_info': user_info}
        def process_pending_response(self, chat_id, message_text, user_info):
            if chat_id in self.pending_responses:
                pending = self.pending_responses.pop(chat_id)
                return f"✅ Processed pending response: {message_text}"
            return None
        def set_user_data(self, user_id, key, value): pass
        def get_user_data(self, user_id, key, default=None): return default
    bot_manager = SimpleManager()

# Command handlers registry
COMMAND_HANDLERS = {}

def load_handlers():
    """Load all command handlers with proper error handling"""
    handlers_to_load = [
        'start',
        'help', 
        'status',
        'time',
        'utils_tools'
    ]
    
    loaded_count = 0
    
    for handler_name in handlers_to_load:
        try:
            module = importlib.import_module(f'bot.handlers.{handler_name}')
            logger.info(f"✅ Successfully imported: {handler_name}")
            
            # Get all functions that start with 'handle_'
            for attr_name in dir(module):
                if attr_name.startswith('handle_'):
                    command_name = attr_name.replace('handle_', '')
                    if command_name != 'demo_response':  # Skip internal handler
                        COMMAND_HANDLERS[f'/{command_name}'] = getattr(module, attr_name)
                        logger.info(f"✅ Loaded command: /{command_name}")
                        loaded_count += 1
                        
        except ImportError as e:
            logger.error(f"❌ Failed to import {handler_name}: {e}")
        except Exception as e:
            logger.error(f"❌ Error loading {handler_name}: {e}")
    
    logger.info(f"🎯 Total commands loaded: {loaded_count}")

# Load handlers at startup
load_handlers()

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    try:
        # Get token from URL parameter OR environment variable
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token required',
                'usage': 'Add ?token=YOUR_BOT_TOKEN to URL or set BOT_TOKEN environment variable',
                'available_commands': list(COMMAND_HANDLERS.keys())
            }), 400

        # Set token in bot manager
        bot_manager.set_token(token)

        if request.method == 'GET':
            return jsonify({
                'status': 'success',
                'message': 'Bot is running on Render!',
                'available_commands': list(COMMAND_HANDLERS.keys()),
                'total_commands': len(COMMAND_HANDLERS),
                'token_received': True,
                'timestamp': datetime.now().isoformat()
            })

        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
            
            # Handle message updates
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text', '').strip()
                user_info = message.get('from', {})
                
                user_name = user_info.get('first_name', 'Unknown')
                logger.info(f"📨 Message from {user_name}: {text}")
                
                # Check for pending responses
                if hasattr(bot_manager, 'process_pending_response'):
                    pending_response = bot_manager.process_pending_response(chat_id, text, user_info)
                    if pending_response:
                        return jsonify(bot_manager.send_message(chat_id, pending_response))
                
                # Process commands
                for command, handler in COMMAND_HANDLERS.items():
                    if text.startswith(command):
                        try:
                            # Call handler with only required parameters
                            response_text = handler(user_info, chat_id, text)
                            return jsonify(bot_manager.send_message(chat_id, response_text))
                        except Exception as e:
                            logger.error(f"Command execution error: {e}")
                            return jsonify(bot_manager.send_message(
                                chat_id, 
                                f"❌ Command error: {str(e)}"
                            ))
                
                # Unknown command response
                if COMMAND_HANDLERS:
                    available_cmds = "\n".join([f"• <code>{cmd}</code>" for cmd in COMMAND_HANDLERS.keys()])
                    response_text = f"❌ <b>Unknown Command:</b> <code>{text}</code>\n\n📋 <b>Available Commands:</b>\n{available_cmds}"
                else:
                    response_text = "❌ <b>No commands loaded.</b> Check server logs."
                
                return jsonify(bot_manager.send_message(chat_id, response_text))
            
            return jsonify({'status': 'ok', 'message': 'No message to process'})

    except Exception as e:
        logger.error(f'🚨 Server error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'total_commands': len(COMMAND_HANDLERS),
        'commands': list(COMMAND_HANDLERS.keys()),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Server starting on port {port}")
    logger.info(f"📊 Loaded {len(COMMAND_HANDLERS)} commands: {list(COMMAND_HANDLERS.keys())}")
    app.run(host='0.0.0.0', port=port, debug=False)
