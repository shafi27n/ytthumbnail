from flask import Flask, request, jsonify
import os
import logging
import importlib
import pkgutil
from datetime import datetime
from bot.core.bot_manager import bot_manager

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auto_discover_handlers():
    """Automatically discover all handler modules with multi-command support"""
    handlers = {}
    
    try:
        handlers_package = importlib.import_module('bot.handlers')
        
        for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
            if module_name != '__init__':
                try:
                    module = importlib.import_module(f'bot.handlers.{module_name}')
                    
                    # Support for multiple commands in one file (name1|name2|name3.py)
                    command_names = module_name.split('|')
                    
                    for command_name in command_names:
                        function_name = f"handle_{command_name}"
                        if hasattr(module, function_name):
                            full_command_name = f"/{command_name}"
                            handlers[full_command_name] = getattr(module, function_name)
                            logger.info(f"✅ Auto-loaded command: {full_command_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error loading handler {module_name}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error discovering handlers: {e}")
    
    return handlers

# Auto-discover all handlers on startup
COMMAND_HANDLERS = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(COMMAND_HANDLERS)}")

def process_inline_button_click(update: dict):
    """Process inline keyboard button clicks"""
    try:
        callback_query = update.get('callback_query', {})
        if not callback_query:
            return None
        
        chat_id = callback_query['message']['chat']['id']
        message_id = callback_query['message']['message_id']
        callback_data = callback_query['data']
        user_info = callback_query['from']
        
        logger.info(f"Inline button clicked by {user_info.get('first_name')}: {callback_data}")
        
        # Answer callback query first
        bot_manager.answer_callback_query(callback_query['id'], "Processing...")
        
        # Process callback data (you can implement your logic here)
        response_text = f"🔘 Button clicked: {callback_data}\n\n👤 User: {user_info.get('first_name')}"
        
        # Edit the original message
        result = bot_manager.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=response_text,
            reply_markup=bot_manager.create_inline_keyboard([
                [bot_manager.create_inline_button("🔄 Click Again", callback_data="click_again")],
                [bot_manager.create_inline_button("❌ Close", callback_data="close_message")]
            ])
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing inline button: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    try:
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if not token:
            return jsonify({
                'error': 'Token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN to URL or set BOT_TOKEN environment variable'
            }), 400

        # Initialize bot manager with token
        bot_manager.set_token(token)

        if request.method == 'GET':
            return jsonify({
                'status': 'Bot is running with ENHANCED AUTO-MODULAR architecture',
                'available_commands': list(COMMAND_HANDLERS.keys()),
                'total_commands': len(COMMAND_HANDLERS),
                'features': [
                    'Auto command discovery',
                    'Multi-command files',
                    'HTML/Markdown formatting',
                    'Media support',
                    'Inline keyboards',
                    'Reply keyboards',
                    'HTTP requests',
                    'User sessions',
                    'Pending responses'
                ],
                'timestamp': datetime.now().isoformat()
            })

        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Handle inline button clicks
            if 'callback_query' in update:
                result = process_inline_button_click(update)
                if result:
                    return jsonify({'ok': True})
            
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                message_text = update['message'].get('text', '').strip()
                user_info = update['message'].get('from', {})
                
                logger.info(f"Message from {user_info.get('first_name')}: {message_text}")
                
                # Check for pending responses first
                pending_response = bot_manager.process_pending_response(chat_id, message_text, user_info)
                if pending_response:
                    return jsonify(bot_manager.send_message(chat_id, pending_response))
                
                # Find and execute command handler
                for command, handler in COMMAND_HANDLERS.items():
                    if message_text.startswith(command):
                        response_text = handler(user_info, chat_id, message_text, bot_manager=bot_manager)
                        return jsonify(bot_manager.send_message(chat_id, response_text))
                
                # Default response for unknown commands
                available_commands = "\n".join([f"• <code>{cmd}</code>" for cmd in COMMAND_HANDLERS.keys()])
                return jsonify(bot_manager.send_message(
                    chat_id, 
                    f"❌ <b>Unknown Command:</b> <code>{message_text}</code>\n\n"
                    f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
                    f"💡 <b>Help:</b> <code>/help</code>"
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
        'user_sessions': len(bot_manager.user_sessions),
        'pending_responses': len(bot_manager.pending_responses),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/debug')
def debug_info():
    """Debug endpoint to see bot state"""
    return jsonify({
        'user_sessions': bot_manager.user_sessions,
        'pending_responses': bot_manager.pending_responses,
        'command_handlers': list(COMMAND_HANDLERS.keys())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
