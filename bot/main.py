from flask import Flask, request, jsonify
import os
import logging
import importlib
import pkgutil
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auto_discover_handlers():
    """Automatically discover all handler modules without any configuration"""
    handlers = {}
    special_handlers = {}
    
    try:
        handlers_package = importlib.import_module('bot.handlers')
        
        for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
            if module_name != '__init__':
                try:
                    module = importlib.import_module(f'bot.handlers.{module_name}')
                    
                    # Regular command handlers
                    function_name = f"handle_{module_name}"
                    if hasattr(module, function_name):
                        command_name = f"/{module_name}"
                        handlers[command_name] = getattr(module, function_name)
                        logger.info(f"✅ Auto-loaded command: {command_name}")
                    
                    # Special handlers
                    special_functions = {
                        'handle_photo': 'photo',
                        'handle_document': 'document', 
                        'handle_video': 'video',
                        'handle_audio': 'audio',
                        'handle_voice': 'voice',
                        'handle_text': 'text',
                        'handle_all_callbacks': 'callbacks'  # নতুন কলব্যাক হ্যান্ডলার
                    }
                    
                    for func_name, handler_type in special_functions.items():
                        if hasattr(module, func_name):
                            special_handlers[handler_type] = getattr(module, func_name)
                            logger.info(f"✅ Auto-loaded special handler: {func_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error loading handler {module_name}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error discovering handlers: {e}")
    
    return handlers, special_handlers

# Auto-discover all handlers on startup
COMMAND_HANDLERS, SPECIAL_HANDLERS = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(COMMAND_HANDLERS)}")
logger.info(f"🎯 Special handlers loaded: {list(SPECIAL_HANDLERS.keys())}")

def send_telegram_message(chat_id, text, parse_mode='HTML'):
    """Send message with HTML parse mode"""
    return {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }

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
                'status': 'Bot is running with AUTO-MODULAR architecture',
                'available_commands': list(COMMAND_HANDLERS.keys()),
                'total_commands': len(COMMAND_HANDLERS),
                'timestamp': datetime.now().isoformat()
            })

        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Handle callback queries (IMPORTANT FIX)
            if 'callback_query' in update:
                callback_data = update['callback_query']['data']
                user_info = update['callback_query']['from']
                chat_id = update['callback_query']['message']['chat']['id']
                message_id = update['callback_query']['message']['message_id']
                
                # Try to find callback handler in all modules
                for module_name in COMMAND_HANDLERS.keys():
                    try:
                        clean_module_name = module_name.replace('/', '')
                        module = importlib.import_module(f'bot.handlers.{clean_module_name}')
                        if hasattr(module, 'handle_all_callbacks'):
                            result = module.handle_all_callbacks(callback_data, user_info, chat_id, message_id)
                            if result:
                                return result
                    except ImportError:
                        continue
                
                # Default callback response
                return jsonify({
                    'method': 'answerCallbackQuery',
                    'callback_query_id': update['callback_query']['id'],
                    'text': 'Action completed'
                })
            
            if 'message' in update:
                return handle_message(update['message'])
            
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'Error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

def handle_message(message):
    """Handle all types of messages"""
    chat_id = message.get('chat', {}).get('id')
    user_info = message.get('from', {})
    message_text = message.get('text', '').strip()
    
    if not chat_id:
        return jsonify({'ok': True})
    
    # Handle text messages and commands
    if 'text' in message:
        # First check if it's a command
        for command, handler in COMMAND_HANDLERS.items():
            if message_text.startswith(command):
                result = handler(user_info, chat_id, message_text)
                return result if result else jsonify({'ok': True})
        
        # Check for text handler (for form sessions)
        if 'text' in SPECIAL_HANDLERS:
            text_response = SPECIAL_HANDLERS['text'](message)
            if text_response:
                return text_response
        
        # Default response for non-command messages
        available_commands = "\n".join([f"• <b>{cmd}</b>" for cmd in COMMAND_HANDLERS.keys()])
        return jsonify(send_telegram_message(
            chat_id, 
            f"👋 <b>Hello {user_info.get('first_name', 'Friend')}!</b>\n\n"
            f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
            f"💡 <b>Need help?</b> Use <b>/menu</b> for interactive menu"
        ))
    
    # Handle media messages
    elif 'photo' in message and 'photo' in SPECIAL_HANDLERS:
        photo_response = SPECIAL_HANDLERS['photo'](message)
        return photo_response if photo_response else jsonify({'ok': True})
    
    # Handle other media types...
    
    else:
        return jsonify(send_telegram_message(
            chat_id,
            "❌ <b>Unsupported Message Type</b>\n\n"
            "💡 <b>Try:</b> <b>/menu</b> for interactive options"
        ))

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(COMMAND_HANDLERS),
        'commands': list(COMMAND_HANDLERS.keys()),
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
