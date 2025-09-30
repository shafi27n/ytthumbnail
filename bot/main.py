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
                        'handle_all_callbacks': 'callbacks'
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
            
            # Handle callback queries
            if 'callback_query' in update:
                return handle_callback_query(update['callback_query'])
            
            if 'message' in update:
                return handle_message(update['message'])
            
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'Error handling request: {e}')
        return jsonify({'error': 'Processing failed'}), 500

def handle_callback_query(callback_query):
    """Handle callback queries from inline keyboards"""
    try:
        callback_data = callback_query.get('data')
        user_info = callback_query.get('from', {})
        message = callback_query.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        message_id = message.get('message_id')
        
        logger.info(f"📨 Callback received: {callback_data} from user {user_info.get('id')}")
        
        if not all([callback_data, chat_id, message_id]):
            return jsonify({'ok': True})
        
        # Try to find callback handler in all modules
        for command_name in COMMAND_HANDLERS.keys():
            try:
                clean_module_name = command_name.replace('/', '')
                module = importlib.import_module(f'bot.handlers.{clean_module_name}')
                if hasattr(module, 'handle_all_callbacks'):
                    result = module.handle_all_callbacks(callback_data, user_info, chat_id, message_id)
                    if result:
                        logger.info(f"✅ Callback handled by {clean_module_name}")
                        return result
            except ImportError:
                continue
            except Exception as e:
                logger.error(f"❌ Error in callback handler {clean_module_name}: {e}")
                continue
        
        # If no handler found, send default response
        logger.warning(f"⚠️ No handler found for callback: {callback_data}")
        return jsonify({
            'method': 'answerCallbackQuery',
            'callback_query_id': callback_query.get('id'),
            'text': 'Action completed'
        })
        
    except Exception as e:
        logger.error(f'❌ Error handling callback: {e}')
        return jsonify({'ok': True})

def handle_message(message):
    """Handle all types of messages"""
    try:
        chat_id = message.get('chat', {}).get('id')
        user_info = message.get('from', {})
        message_text = message.get('text', '').strip()
        
        if not chat_id:
            return jsonify({'ok': True})
        
        logger.info(f"📨 Message received from {user_info.get('first_name')}: {message_text}")
        
        # Handle text messages and commands
        if 'text' in message:
            # First check if it's a command
            for command, handler in COMMAND_HANDLERS.items():
                if message_text.startswith(command):
                    logger.info(f"✅ Command matched: {command}")
                    result = handler(user_info, chat_id, message_text)
                    
                    # Handle different return types
                    if isinstance(result, str):
                        # If handler returns string, send as message
                        return jsonify(send_telegram_message(chat_id, result, parse_mode='HTML'))
                    elif result is not None:
                        # If handler returns JSON response
                        return result
                    else:
                        # If handler returns None, send default response
                        return jsonify({'ok': True})
            
            # Check for text handler (for form sessions)
            if 'text' in SPECIAL_HANDLERS:
                logger.info("🔄 Checking text handler for session")
                text_response = SPECIAL_HANDLERS['text'](message)
                if text_response:
                    return text_response
            
            # Default response for non-command messages
            return jsonify(send_telegram_message(
                chat_id, 
                f"👋 <b>Hello {user_info.get('first_name', 'Friend')}!</b>\n\n"
                f"💡 <b>Available commands:</b> /start, /menu, /form, /help\n\n"
                f"📱 <b>Try:</b> <b>/menu</b> for interactive options"
            ))
        
        # Handle media messages with special handlers
        media_handlers = {
            'photo': 'photo',
            'document': 'document',
            'video': 'video', 
            'audio': 'audio',
            'voice': 'voice'
        }
        
        for media_type, handler_key in media_handlers.items():
            if media_type in message and handler_key in SPECIAL_HANDLERS:
                logger.info(f"🖼️ Handling {media_type} message")
                media_response = SPECIAL_HANDLERS[handler_key](message)
                if media_response:
                    return media_response
        
        # Unknown message type
        return jsonify(send_telegram_message(
            chat_id,
            "❌ <b>Unsupported Message Type</b>\n\n"
            "📋 <b>I can handle:</b>\n"
            "• Text messages and commands\n"
            "• Photos, videos, documents\n" 
            "• Audio, voice messages\n\n"
            "💡 <b>Try:</b> <b>/menu</b> for interactive options"
        ))
        
    except Exception as e:
        logger.error(f'❌ Error handling message: {e}')
        return jsonify(send_telegram_message(
            message.get('chat', {}).get('id'),
            "❌ <b>Error processing your message</b>\n\n"
            "Please try again or use /menu for options"
        ))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(COMMAND_HANDLERS),
        'commands': list(COMMAND_HANDLERS.keys()),
        'special_handlers': list(SPECIAL_HANDLERS.keys()),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/debug/handlers', methods=['GET'])
def debug_handlers():
    """Debug endpoint to see loaded handlers"""
    return jsonify({
        'command_handlers': list(COMMAND_HANDLERS.keys()),
        'special_handlers': list(SPECIAL_HANDLERS.keys()),
        'total_loaded': len(COMMAND_HANDLERS),
        'status': 'working'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Starting Telegram Bot on port {port}")
    logger.info(f"📋 Loaded {len(COMMAND_HANDLERS)} commands: {list(COMMAND_HANDLERS.keys())}")
    logger.info(f"🔧 Special handlers: {list(SPECIAL_HANDLERS.keys())}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
