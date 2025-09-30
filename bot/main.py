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
    
    try:
        handlers_package = importlib.import_module('bot.handlers')
        
        for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
            if module_name != '__init__':
                try:
                    module = importlib.import_module(f'bot.handlers.{module_name}')
                    
                    function_name = f"handle_{module_name}"
                    if hasattr(module, function_name):
                        command_name = f"/{module_name}"
                        handlers[command_name] = getattr(module, function_name)
                        logger.info(f"✅ Auto-loaded command: {command_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error loading handler {module_name}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error discovering handlers: {e}")
    
    return handlers

# Auto-discover all handlers on startup
COMMAND_HANDLERS = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(COMMAND_HANDLERS)}")

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
                chat_id = update['message']['chat']['id']
                message_text = update['message'].get('text', '').strip()
                user_info = update['message'].get('from', {})
                
                logger.info(f"Message from {user_info.get('first_name')}: {message_text}")
                
                # Find and execute command handler
                for command, handler in COMMAND_HANDLERS.items():
                    if message_text.startswith(command):
                        response_text = handler(user_info, chat_id, message_text)
                        return jsonify(send_telegram_message(chat_id, response_text))
                
                # Default response for unknown commands
                available_commands = "\n".join([f"• <b>{cmd}</b>" for cmd in COMMAND_HANDLERS.keys()])
                return jsonify(send_telegram_message(
                    chat_id, 
                    f"❌ <b>Unknown Command:</b> <b>{message_text}</b>\n\n"
                    f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
                    f"💡 <b>Help:</b> <b>/help</b>"
                ))
            
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'Error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

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
