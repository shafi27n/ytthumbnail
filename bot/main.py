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
                        'handle_text': 'text'  # নতুন text handler
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
                response_text = handler(user_info, chat_id, message_text)
                return jsonify(send_telegram_message(chat_id, response_text))
        
        # Check for text handler (for upload sessions)
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
            f"💡 <b>Need help?</b> <b>/help</b>\n"
            f"📸 <b>Want to upload?</b> <b>/upload</b>"
        ))
    
    # Handle media messages
    elif 'photo' in message and 'photo' in SPECIAL_HANDLERS:
        return SPECIAL_HANDLERS['photo'](message)
    
    elif 'document' in message and 'document' in SPECIAL_HANDLERS:
        return SPECIAL_HANDLERS['document'](message)
    
    elif 'video' in message and 'video' in SPECIAL_HANDLERS:
        return SPECIAL_HANDLERS['video'](message)
    
    elif 'audio' in message and 'audio' in SPECIAL_HANDLERS:
        return SPECIAL_HANDLERS['audio'](message)
    
    elif 'voice' in message and 'voice' in SPECIAL_HANDLERS:
        return SPECIAL_HANDLERS['voice'](message)
    
    else:
        # Unknown message type
        return jsonify(send_telegram_message(
            chat_id,
            "❌ <b>Unsupported Message Type</b>\n\n"
            "📋 <b>I can handle:</b>\n"
            "• Text messages and commands\n"
            "• Photos, videos, documents\n" 
            "• Audio, voice messages\n\n"
            "💡 <b>Try:</b> <b>/help</b>"
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
