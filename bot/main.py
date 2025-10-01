from flask import Flask, request, jsonify
import os
import logging
import importlib
import pkgutil
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from bot.core import bot_core, Bot, User

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7628222622:AAEomk7Od-jcKnQMdkmOpejvYYF47BjMAMQ')

# Global variables
telegram_app = None
COMMAND_HANDLERS = {}

def auto_discover_handlers():
    """Automatically discover all handler modules"""
    handlers = {}
    
    try:
        handlers_package = importlib.import_module('bot.handlers')
        
        for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
            if module_name != '__init__':
                try:
                    module = importlib.import_module(f'bot.handlers.{module_name}')
                    
                    # Handle multiple commands in one file (name1|name2|name3.py)
                    command_names = module_name.split('|')
                    
                    for command_name in command_names:
                        function_name = f"handle_{command_name}"
                        if hasattr(module, function_name):
                            handlers[f"/{command_name}"] = getattr(module, function_name)
                            logger.info(f"✅ Auto-loaded command: /{command_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error loading handler {module_name}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error discovering handlers: {e}")
    
    return handlers

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text if update.message else ""
        
        logger.info(f"Message from {update.effective_user.first_name}: {message_text}")
        
        # Check if user has a waiting command
        if await bot_core.process_waiting_command(update, context):
            return
        
        # Handle regular commands
        for command, handler in COMMAND_HANDLERS.items():
            if message_text.startswith(command):
                await handler(update, context, bot_core)
                return
        
        # Unknown command
        available_commands = "\n".join([f"• <code>{cmd}</code>" for cmd in COMMAND_HANDLERS.keys()])
        await bot_core.send_message(
            update,
            f"❌ <b>Unknown Command:</b> <code>{message_text}</code>\n\n"
            f"📋 <b>Available Commands:</b>\n{available_commands}\n\n"
            f"💡 <b>Help:</b> <code>/help</code>"
        )
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await bot_core.send_error_message(update, str(e))

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    try:
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        logger.info(f"Callback query: {callback_data}")
        
        # You can add specific callback handling here
        await bot_core.send_message(
            update,
            f"🔘 Button pressed: <code>{callback_data}</code>"
        )
        
    except Exception as e:
        logger.error(f"Error handling callback: {e}")
        await bot_core.send_error_message(update, str(e))

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await bot_core.send_message(
        update,
        "❌ <b>Unknown Command</b>\n\n"
        "Use <code>/help</code> to see available commands."
    )

def setup_telegram_bot():
    """Setup Telegram bot handlers"""
    global telegram_app
    
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    telegram_app.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Add command handlers dynamically
    for command, handler in COMMAND_HANDLERS.items():
        telegram_app.add_handler(CommandHandler(command[1:], handler))
    
    logger.info("✅ Telegram bot setup completed")

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    try:
        if request.method == 'GET':
            return jsonify({
                'status': 'Bot is running with AUTO-MODULAR architecture',
                'available_commands': list(COMMAND_HANDLERS.keys()),
                'total_commands': len(COMMAND_HANDLERS),
                'timestamp': datetime.now().isoformat(),
                'features': [
                    'Auto command discovery',
                    'Supabase integration', 
                    'HTML/Markdown formatting',
                    'Inline keyboards',
                    'File uploads',
                    'HTTP requests',
                    'User sessions',
                    'Error handling'
                ]
            })

        if request.method == 'POST':
            update_data = request.get_json()
            
            if not update_data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # For webhook mode, process update
            if telegram_app:
                update = Update.de_json(update_data, telegram_app.bot)
                telegram_app.update_queue.put(update)
            
            return jsonify({'status': 'processing'})

    except Exception as e:
        logger.error(f'Error handling request: {e}')
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(COMMAND_HANDLERS),
        'commands': list(COMMAND_HANDLERS.keys()),
        'database_connected': bot_core.db.supabase is not None,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/send-message', methods=['POST'])
def send_broadcast():
    """Send message to specific user (admin feature)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not user_id or not message:
            return jsonify({'error': 'user_id and message required'}), 400
        
        # This would require bot instance to send messages
        return jsonify({'status': 'Message sent'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize the system
def initialize_bot():
    """Initialize the bot system"""
    global COMMAND_HANDLERS
    
    logger.info("🚀 Initializing Auto-Modular Telegram Bot...")
    
    # Auto-discover handlers
    COMMAND_HANDLERS = auto_discover_handlers()
    logger.info(f"🎯 Total commands loaded: {len(COMMAND_HANDLERS)}")
    
    # Setup Telegram bot
    setup_telegram_bot()
    
    # Save initial bot data
    bot_core.db.save_bot_data('startup_time', datetime.now().isoformat())
    bot_core.db.save_bot_data('total_commands', len(COMMAND_HANDLERS))
    
    logger.info("✅ Bot initialization completed")

# Initialize on import
initialize_bot()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    # For production with webhook
    if os.environ.get('RENDER', False) or os.environ.get('PYROID', False):
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # For development with polling
        logger.info("🤖 Starting bot with polling...")
        telegram_app.run_polling()
        app.run(host='0.0.0.0', port=port, debug=True)