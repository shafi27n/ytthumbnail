from flask import Flask, request, jsonify
import os
import logging
import importlib
import pkgutil
from datetime import datetime
import requests

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
                    
                    # Regular command handlers (handle_commandname)
                    function_name = f"handle_{module_name}"
                    if hasattr(module, function_name):
                        command_name = f"/{module_name}"
                        handlers[command_name] = getattr(module, function_name)
                        logger.info(f"✅ Auto-loaded command: {command_name}")
                    
                    # Special handlers (handle_photo, handle_document, etc.)
                    special_functions = {
                        'handle_photo': 'photo',
                        'handle_document': 'document',
                        'handle_video': 'video',
                        'handle_audio': 'audio',
                        'handle_voice': 'voice',
                        'handle_sticker': 'sticker',
                        'handle_location': 'location',
                        'handle_contact': 'contact'
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

def send_telegram_photo(chat_id, photo_url, caption=None, parse_mode='HTML'):
    """Send photo with caption"""
    photo_data = {
        'method': 'sendPhoto',
        'chat_id': chat_id,
        'photo': photo_url
    }
    
    if caption:
        photo_data['caption'] = caption
        photo_data['parse_mode'] = parse_mode
        
    return photo_data

def get_telegram_file_url(file_id):
    """Get direct URL for Telegram file"""
    try:
        bot_token = os.environ.get('BOT_TOKEN')
        file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        file_info_response = requests.get(file_info_url).json()
        
        if file_info_response.get('ok'):
            file_path = file_info_response['result']['file_path']
            return f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        return None
    except Exception as e:
        logger.error(f"Error getting file URL: {e}")
        return None

def forward_to_channel(chat_id, message_id, target_channel='@refffrrr'):
    """Forward message to channel"""
    try:
        bot_token = os.environ.get('BOT_TOKEN')
        forward_data = {
            'chat_id': target_channel,
            'from_chat_id': chat_id,
            'message_id': message_id
        }
        
        forward_url = f"https://api.telegram.org/bot{bot_token}/forwardMessage"
        forward_response = requests.post(forward_url, json=forward_data).json()
        return forward_response
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        return {'ok': False, 'description': str(e)}

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
                'status': 'Bot is running with COMPLETE AUTO-MODULAR architecture',
                'available_commands': list(COMMAND_HANDLERS.keys()),
                'special_handlers': list(SPECIAL_HANDLERS.keys()),
                'total_commands': len(COMMAND_HANDLERS),
                'timestamp': datetime.now().isoformat()
            })

        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            logger.info(f"📨 Update received: {update.keys()}")
            
            # Handle different types of updates
            if 'message' in update:
                return handle_message(update['message'])
            elif 'edited_message' in update:
                return handle_message(update['edited_message'])
            elif 'channel_post' in update:
                return handle_message(update['channel_post'])
            else:
                logger.info("🔄 Other update type received")
                return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'❌ Main Error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

def handle_message(message):
    """Handle all types of messages"""
    chat_id = message.get('chat', {}).get('id')
    user_info = message.get('from', {})
    message_id = message.get('message_id')
    
    if not chat_id:
        return jsonify({'ok': True})
    
    # Handle text messages and commands
    if 'text' in message:
        return handle_text_message(message, chat_id, user_info)
    
    # Handle media messages
    elif 'photo' in message:
        return handle_media_message(message, chat_id, user_info, 'photo')
    
    elif 'document' in message:
        return handle_media_message(message, chat_id, user_info, 'document')
    
    elif 'video' in message:
        return handle_media_message(message, chat_id, user_info, 'video')
    
    elif 'audio' in message:
        return handle_media_message(message, chat_id, user_info, 'audio')
    
    elif 'voice' in message:
        return handle_media_message(message, chat_id, user_info, 'voice')
    
    elif 'sticker' in message:
        return handle_media_message(message, chat_id, user_info, 'sticker')
    
    elif 'location' in message:
        return handle_media_message(message, chat_id, user_info, 'location')
    
    elif 'contact' in message:
        return handle_media_message(message, chat_id, user_info, 'contact')
    
    else:
        # Unknown message type
        logger.info(f"🔍 Unknown message type: {message.keys()}")
        return jsonify(send_telegram_message(
            chat_id,
            "❌ <b>Unsupported Message Type</b>\n\n"
            "📋 <b>I can handle:</b>\n"
            "• Text messages and commands\n"
            "• Photos, videos, documents\n" 
            "• Audio, voice messages\n"
            "• Stickers, locations, contacts\n\n"
            "💡 <b>Try:</b> <code>/help</code>"
        ))

def handle_text_message(message, chat_id, user_info):
    """Handle text messages and commands"""
    message_text = message.get('text', '').strip()
    first_name = user_info.get('first_name', 'Friend')
    
    logger.info(f"💬 Text from {first_name}: {message_text}")
    
    # Find and execute command handler
    for command, handler in COMMAND_HANDLERS.items():
        if message_text.startswith(command):
            response_text = handler(user_info, chat_id, message_text)
            return jsonify(send_telegram_message(chat_id, response_text))
    
    # Default response for non-command messages
    available_commands = "\n".join([f"• <code>{cmd}</code>" for cmd in COMMAND_HANDLERS.keys()])
    return jsonify(send_telegram_message(
        chat_id, 
        f"👋 <b>Hello {first_name}!</b>\n\n"
        f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
        f"💡 <b>Need help?</b> <code>/help</code>\n"
        f"📸 <b>Want to upload?</b> <code>/upload</code>"
    ))

def handle_media_message(message, chat_id, user_info, media_type):
    """Handle all types of media messages"""
    logger.info(f"📁 {media_type.capitalize()} received from {user_info.get('first_name')}")
    
    # Check if there's a special handler for this media type
    if media_type in SPECIAL_HANDLERS:
        try:
            handler_response = SPECIAL_HANDLERS[media_type](message)
            if handler_response:
                return handler_response
        except Exception as e:
            logger.error(f"❌ Error in {media_type} handler: {e}")
    
    # Default media handler
    first_name = user_info.get('first_name', 'Friend')
    file_id = get_file_id_from_message(message, media_type)
    file_url = get_telegram_file_url(file_id) if file_id else None
    
    media_info = {
        'photo': {'emoji': '📸', 'name': 'Photo'},
        'document': {'emoji': '📄', 'name': 'Document'}, 
        'video': {'emoji': '🎥', 'name': 'Video'},
        'audio': {'emoji': '🎵', 'name': 'Audio'},
        'voice': {'emoji': '🎤', 'name': 'Voice Message'},
        'sticker': {'emoji': '🤡', 'name': 'Sticker'},
        'location': {'emoji': '📍', 'name': 'Location'},
        'contact': {'emoji': '👤', 'name': 'Contact'}
    }
    
    media_data = media_info.get(media_type, {'emoji': '📁', 'name': 'File'})
    
    response_text = f"""
{media_data['emoji']} <b>{media_data['name']} Received!</b>

👤 <b>From:</b> {first_name}
📦 <b>Type:</b> {media_data['name']}
{f'🔗 <b>File URL:</b> <code>{file_url}</code>' if file_url else ''}
🆔 <b>File ID:</b> <code>{file_id}</code>

💡 <b>Need special handling?</b>
Add a handler for <code>{media_type}</code> in handlers folder!

📋 <b>Available commands:</b> <code>/help</code>
    """
    
    return jsonify(send_telegram_message(chat_id, response_text))

def get_file_id_from_message(message, media_type):
    """Extract file ID from different media types"""
    if media_type == 'photo':
        # Get the highest quality photo
        photos = message.get('photo', [])
        return photos[-1].get('file_id') if photos else None
    elif media_type in ['document', 'video', 'audio', 'voice', 'sticker']:
        return message.get(media_type, {}).get('file_id')
    else:
        return None

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(COMMAND_HANDLERS),
        'commands': list(COMMAND_HANDLERS.keys()),
        'special_handlers': list(SPECIAL_HANDLERS.keys()),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/test')
def test_route():
    return jsonify({
        'message': 'Bot is working!',
        'system': 'Complete Auto-Modular Telegram Bot',
        'handlers_loaded': len(COMMAND_HANDLERS),
        'special_handlers': len(SPECIAL_HANDLERS)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
