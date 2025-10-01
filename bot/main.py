from flask import Flask, request, jsonify
import os
import logging
import importlib
import pkgutil
from datetime import datetime
import requests
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global session storage for all modules
SESSIONS = {}

def auto_discover_handlers():
    """Automatically discover all handler modules without any configuration"""
    handlers = {}
    special_handlers = {
        'text': [],
        'photo': [],
        'document': [],
        'video': [],
        'audio': [],
        'voice': [],
        'callbacks': []
    }
    
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
                    
                    # Special handlers - collect all from all modules
                    special_functions = {
                        'handle_text': 'text',
                        'handle_photo': 'photo',
                        'handle_document': 'document', 
                        'handle_video': 'video',
                        'handle_audio': 'audio',
                        'handle_voice': 'voice',
                        'handle_all_callbacks': 'callbacks'
                    }
                    
                    for func_name, handler_type in special_functions.items():
                        if hasattr(module, func_name):
                            handler_func = getattr(module, func_name)
                            special_handlers[handler_type].append(handler_func)
                            logger.info(f"✅ Auto-loaded special handler: {module_name}.{func_name}")
                    
                    # Import SESSIONS if module has its own
                    if hasattr(module, 'SESSIONS'):
                        module_sessions = getattr(module, 'SESSIONS')
                        SESSIONS.update(module_sessions)
                        logger.info(f"✅ Loaded sessions from {module_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error loading handler {module_name}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error discovering handlers: {e}")
    
    return handlers, special_handlers

# Auto-discover all handlers on startup
COMMAND_HANDLERS, SPECIAL_HANDLERS = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(COMMAND_HANDLERS)}")
logger.info(f"🎯 Commands: {list(COMMAND_HANDLERS.keys())}")
logger.info(f"🔧 Special handlers: {[f'{k}: {len(v)}' for k, v in SPECIAL_HANDLERS.items()]}")

def send_telegram_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    """Send message with HTML parse mode"""
    message_data = {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    if reply_markup:
        message_data['reply_markup'] = reply_markup
        
    return message_data

def execute_telegram_method(method_data):
    """Execute Telegram API method"""
    try:
        bot_token = os.environ.get('BOT_TOKEN')
        if not bot_token:
            logger.error("❌ BOT_TOKEN not found in environment variables")
            return None
            
        url = f"https://api.telegram.org/bot{bot_token}/{method_data['method']}"
        headers = {'Content-Type': 'application/json'}
        
        # Remove method from data as it's in URL
        data = method_data.copy()
        method_name = data.pop('method')
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Telegram API {method_name} successful")
            return response.json()
        else:
            logger.error(f"❌ Telegram API {method_name} error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error executing Telegram method: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    """Main webhook handler"""
    try:
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if not token:
            return jsonify({
                'error': 'Token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN to URL or set BOT_TOKEN environment variable',
                'available_commands': list(COMMAND_HANDLERS.keys()),
                'timestamp': datetime.now().isoformat()
            }), 400

        if request.method == 'GET':
            return jsonify({
                'status': 'Bot is running with AUTO-MODULAR architecture',
                'available_commands': list(COMMAND_HANDLERS.keys()),
                'total_commands': len(COMMAND_HANDLERS),
                'special_handlers': {k: len(v) for k, v in SPECIAL_HANDLERS.items()},
                'active_sessions': len(SESSIONS),
                'timestamp': datetime.now().isoformat()
            })

        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            logger.info(f"📨 Received update: {update.keys()}")
            
            # Handle callback queries
            if 'callback_query' in update:
                result = handle_callback_query(update['callback_query'])
                if result:
                    return result
            
            # Handle messages
            if 'message' in update:
                result = handle_message(update['message'])
                if result:
                    return result
            
            return jsonify({'ok': True, 'handled': True})

    except Exception as e:
        logger.error(f'❌ Error handling request: {e}')
        return jsonify({'error': 'Processing failed'}), 500

def handle_callback_query(callback_query):
    """Handle callback queries from inline keyboards"""
    try:
        callback_data = callback_query.get('data')
        user_info = callback_query.get('from', {})
        message = callback_query.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        message_id = message.get('message_id')
        callback_query_id = callback_query.get('id')
        
        logger.info(f"🔄 Callback received: {callback_data} from user {user_info.get('id')}")
        
        if not all([callback_data, chat_id, message_id, callback_query_id]):
            return jsonify({'ok': True})
        
        # First, answer the callback query to remove loading state
        answer_data = {
            'method': 'answerCallbackQuery',
            'callback_query_id': callback_query_id,
            'text': 'Processing...'
        }
        execute_telegram_method(answer_data)
        
        # Try all callback handlers from all modules
        callback_handled = False
        for callback_handler in SPECIAL_HANDLERS.get('callbacks', []):
            try:
                result = callback_handler(callback_data, user_info, chat_id, message_id)
                if result:
                    callback_handled = True
                    # If handler returns JSON response, execute it
                    if isinstance(result, dict):
                        execute_telegram_method(result)
                    elif hasattr(result, 'json'):
                        execute_telegram_method(result.get_json())
                    break
            except Exception as e:
                logger.error(f"❌ Error in callback handler: {e}")
                continue
        
        if not callback_handled:
            logger.warning(f"⚠️ No handler found for callback: {callback_data}")
            # Send default response for unhandled callbacks
            execute_telegram_method(send_telegram_message(
                chat_id, 
                f"❌ <b>Action not implemented</b>\n\nCallback: <code>{callback_data}</code>",
                parse_mode='HTML'
            ))
        
        return jsonify({'ok': True})
        
    except Exception as e:
        logger.error(f'❌ Error handling callback: {e}')
        return jsonify({'ok': True})

def handle_message(message):
    """Handle all types of messages"""
    try:
        chat_id = message.get('chat', {}).get('id')
        user_info = message.get('from', {})
        message_text = message.get('text', '').strip()
        user_id = user_info.get('id')
        
        if not chat_id:
            return jsonify({'ok': True})
        
        logger.info(f"📨 Message from {user_info.get('first_name')} ({user_id}): {message_text}")
        
        # Check if user has active session
        if user_id in SESSIONS:
            session_data = SESSIONS[user_id]
            logger.info(f"🎯 Active session found: {session_data}")
        
        # Handle text messages and commands
        if 'text' in message:
            # First check if it's a command
            for command, handler in COMMAND_HANDLERS.items():
                if message_text.startswith(command):
                    logger.info(f"✅ Command matched: {command}")
                    
                    # Execute command handler
                    result = handler(user_info, chat_id, message_text)
                    
                    # Handle different return types
                    if isinstance(result, str):
                        # String response - send as message
                        execute_telegram_method(send_telegram_message(chat_id, result, parse_mode='HTML'))
                    elif isinstance(result, dict):
                        # Dict response - execute as Telegram method
                        execute_telegram_method(result)
                    elif hasattr(result, 'json'):
                        # Flask jsonify response
                        execute_telegram_method(result.get_json())
                    
                    return jsonify({'ok': True})
            
            # Check for text handlers (for sessions and other processing)
            text_handled = False
            for text_handler in SPECIAL_HANDLERS.get('text', []):
                try:
                    result = text_handler(message)
                    if result:
                        text_handled = True
                        if isinstance(result, dict):
                            execute_telegram_method(result)
                        elif hasattr(result, 'json'):
                            execute_telegram_method(result.get_json())
                        break
                except Exception as e:
                    logger.error(f"❌ Error in text handler: {e}")
                    continue
            
            if text_handled:
                return jsonify({'ok': True})
            
            # Default response for non-command messages
            if not text_handled:
                available_commands = "\n".join([f"• <b>{cmd}</b>" for cmd in COMMAND_HANDLERS.keys()])
                execute_telegram_method(send_telegram_message(
                    chat_id, 
                    f"👋 <b>Hello {user_info.get('first_name', 'Friend')}!</b>\n\n"
                    f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
                    f"💡 <b>Try:</b> <b>/menu</b> for interactive options",
                    parse_mode='HTML'
                ))
        
        # Handle media messages with special handlers
        media_handlers = {
            'photo': SPECIAL_HANDLERS.get('photo', []),
            'document': SPECIAL_HANDLERS.get('document', []),
            'video': SPECIAL_HANDLERS.get('video', []),
            'audio': SPECIAL_HANDLERS.get('audio', []),
            'voice': SPECIAL_HANDLERS.get('voice', [])
        }
        
        for media_type, handlers in media_handlers.items():
            if media_type in message and handlers:
                logger.info(f"🖼️ Handling {media_type} message")
                media_handled = False
                for media_handler in handlers:
                    try:
                        result = media_handler(message)
                        if result:
                            media_handled = True
                            if isinstance(result, dict):
                                execute_telegram_method(result)
                            elif hasattr(result, 'json'):
                                execute_telegram_method(result.get_json())
                            break
                    except Exception as e:
                        logger.error(f"❌ Error in {media_type} handler: {e}")
                        continue
                
                if media_handled:
                    return jsonify({'ok': True})
        
        # Unknown message type
        if 'text' not in message and not any(media_type in message for media_type in media_handlers.keys()):
            execute_telegram_method(send_telegram_message(
                chat_id,
                "❌ <b>Unsupported Message Type</b>\n\n"
                "📋 <b>I can handle:</b>\n"
                "• Text messages and commands\n"
                "• Photos, videos, documents\n" 
                "• Audio, voice messages\n\n"
                "💡 <b>Try:</b> <b>/menu</b> for interactive options",
                parse_mode='HTML'
            ))
        
        return jsonify({'ok': True})
        
    except Exception as e:
        logger.error(f'❌ Error handling message: {e}')
        try:
            execute_telegram_method(send_telegram_message(
                message.get('chat', {}).get('id'),
                "❌ <b>Error processing your message</b>\n\n"
                "Please try again or use /menu for options",
                parse_mode='HTML'
            ))
        except:
            pass
        return jsonify({'ok': True})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(COMMAND_HANDLERS),
        'commands': list(COMMAND_HANDLERS.keys()),
        'special_handlers': {k: len(v) for k, v in SPECIAL_HANDLERS.items()},
        'active_sessions': len(SESSIONS),
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - app_start_time
    }), 200

@app.route('/debug/handlers', methods=['GET'])
def debug_handlers():
    """Debug endpoint to see loaded handlers"""
    handler_details = {}
    
    for command, handler in COMMAND_HANDLERS.items():
        handler_details[command] = {
            'function': handler.__name__,
            'module': handler.__module__
        }
    
    special_details = {}
    for handler_type, handlers in SPECIAL_HANDLERS.items():
        special_details[handler_type] = [
            f"{h.__module__}.{h.__name__}" for h in handlers
        ]
    
    return jsonify({
        'command_handlers': handler_details,
        'special_handlers': special_details,
        'sessions': SESSIONS,
        'total_loaded': len(COMMAND_HANDLERS),
        'status': 'working'
    })

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions"""
    return jsonify({
        'active_sessions': len(SESSIONS),
        'sessions': SESSIONS,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/sessions/clear', methods=['POST'])
def clear_sessions():
    """Clear all sessions"""
    global SESSIONS
    session_count = len(SESSIONS)
    SESSIONS = {}
    return jsonify({
        'message': f'Cleared {session_count} sessions',
        'sessions_remaining': 0
    })

# Store app start time
app_start_time = time.time()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Starting Telegram Bot on port {port}")
    logger.info(f"📋 Loaded {len(COMMAND_HANDLERS)} commands: {list(COMMAND_HANDLERS.keys())}")
    logger.info(f"🔧 Special handlers: {[f'{k}: {len(v)}' for k, v in SPECIAL_HANDLERS.items()]}")
    logger.info(f"💾 Global sessions initialized")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
