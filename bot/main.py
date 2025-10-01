from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime
from bot.core.bot_manager import BotManager, UserManager

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot manager (without token initially)
bot_manager = BotManager()

def get_bot_manager(token=None):
    """Get or create bot manager with token"""
    if token:
        bot_manager.bot_token = token
        bot_manager.base_url = f"https://api.telegram.org/bot{token}"
    return bot_manager

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    try:
        # Get token from URL parameter or environment
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if not token:
            return jsonify({
                'error': 'Token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN to URL or set BOT_TOKEN environment variable',
                'example': 'https://your-app.render.com/?token=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                'setup_guide': '1. Get token from @BotFather\n2. Use: your-url.render.com/?token=YOUR_BOT_TOKEN'
            }), 400

        # Initialize bot manager with token
        current_bot_manager = get_bot_manager(token)
        
        if request.method == 'GET':
            return jsonify({
                'status': 'Bot is running with AUTO-MODULAR SUPER SYSTEM',
                'token_provided': '✅ Yes' if token else '❌ No',
                'token_length': len(token) if token else 0,
                'available_commands': list(current_bot_manager.command_handlers.keys()),
                'total_commands': len(current_bot_manager.command_handlers),
                'timestamp': datetime.now().isoformat(),
                'webhook_url': f'{request.base_url}?token={token}',
                'features': [
                    'Auto command discovery',
                    'Supabase integration', 
                    'User data management',
                    'Bot data management',
                    'Next command handling',
                    'Multi-command files',
                    'Full Telegram API support'
                ]
            })

        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            if 'message' in update:
                return handle_message(update, current_bot_manager)
            
            if 'callback_query' in update:
                return handle_callback_query(update, current_bot_manager)
            
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'Error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

def handle_message(update, bot_manager):
    """Handle incoming messages"""
    chat_id = update['message']['chat']['id']
    message_text = update['message'].get('text', '').strip()
    user_info = update['message'].get('from', {})
    user_id = user_info.get('id')
    message_id = update['message'].get('message_id')
    
    logger.info(f"Message from {user_info.get('first_name')}: {message_text}")
    
    # Initialize user manager
    user_manager = UserManager(user_id)
    
    # Check if user has a waiting command
    waiting_command = bot_manager.get_waiting_command(user_id)
    if waiting_command:
        response = bot_manager.run_command(waiting_command, user_info, chat_id, message_text)
        return format_response(response, chat_id)
    
    # Find and execute command handler
    for command in bot_manager.command_handlers.keys():
        if message_text.startswith(command):
            response = bot_manager.run_command(command, user_info, chat_id, message_text)
            return format_response(response, chat_id)
    
    # Default response for unknown commands
    available_commands = "\n".join([f"• <code>{cmd}</code>" for cmd in bot_manager.command_handlers.keys()])
    return jsonify({
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': f"❌ <b>Unknown Command:</b> <code>{message_text}</code>\n\n"
                f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
                f"💡 <b>Help:</b> <code>/help</code>",
        'parse_mode': 'HTML'
    })

def handle_callback_query(update, bot_manager):
    """Handle inline button callbacks"""
    callback_query = update['callback_query']
    data = callback_query.get('data', '')
    user_info = callback_query.get('from', {})
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    
    logger.info(f"Callback from {user_info.get('first_name')}: {data}")
    
    # You can implement callback handling logic here
    # For now, just acknowledge the callback
    return jsonify({
        'method': 'answerCallbackQuery',
        'callback_query_id': callback_query['id'],
        'text': 'Callback received!'
    })

def format_response(response, chat_id):
    """Format response for Telegram API"""
    if isinstance(response, str):
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': response,
            'parse_mode': 'HTML'
        })
    elif isinstance(response, dict):
        response['chat_id'] = chat_id
        if 'parse_mode' not in response:
            response['parse_mode'] = 'HTML'
        return jsonify(response)
    else:
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': '✅ Command executed successfully',
            'parse_mode': 'HTML'
        })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(bot_manager.command_handlers),
        'commands': list(bot_manager.command_handlers.keys()),
        'waiting_users': len(bot_manager.waiting_commands),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/setup')
def setup_guide():
    """Setup guide for Render deployment"""
    return jsonify({
        'title': '🚀 Telegram Bot Setup Guide for Render',
        'steps': [
            '1. Fork this repository to your GitHub',
            '2. Go to render.com and create new Web Service',
            '3. Connect your GitHub repository',
            '4. Use these build settings:',
            '   - Build Command: pip install -r requirements.txt',
            '   - Start Command: gunicorn bot.main:app',
            '5. Add environment variable (optional):',
            '   - Key: BOT_TOKEN, Value: your_bot_token',
            '6. Deploy!',
            '7. Set webhook URL in Telegram:',
            '   - https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_RENDER_URL>?token=<YOUR_TOKEN>'
        ],
        'usage_methods': [
            'Method 1 - URL Token: https://your-app.render.com/?token=YOUR_BOT_TOKEN',
            'Method 2 - Environment Variable: Set BOT_TOKEN in Render dashboard',
            'Method 3 - Webhook: Set webhook with token in URL'
        ]
    })

# Auto-discover handlers on startup
if __name__ == '__main__':
    bot_manager.auto_discover_handlers()
    logger.info(f"🎯 Total commands loaded: {len(bot_manager.command_handlers)}")
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # For gunicorn
    bot_manager.auto_discover_handlers()
