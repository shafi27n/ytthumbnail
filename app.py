from flask import Flask, request, jsonify
import os
import logging
import importlib
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7628222622:AAEomk7Od-jcKnQMdkmOpejvYYF47BjMAMQ')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
PORT = int(os.environ.get('PORT', 10000))

class SimpleBot:
    def __init__(self):
        self.waiting_commands = {}
        # Use create_task for async operations
        self.app = None
        self._initialize_app()
    
    def _initialize_app(self):
        """Initialize telegram app"""
        try:
            self.app = Application.builder().token(BOT_TOKEN).build()
            
            # Add message handler
            self.app.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
            )
            
            logger.info("✅ Telegram app initialized")
        except Exception as e:
            logger.error(f"❌ App initialization failed: {e}")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        try:
            user_id = update.effective_user.id
            text = update.message.text
            
            logger.info(f"📨 Message from {user_id}: {text}")
            
            # Check waiting commands first
            if user_id in self.waiting_commands:
                command = self.waiting_commands[user_id]
                del self.waiting_commands[user_id]
                context.user_data['user_response'] = text
                await self.run_command(command, update, context)
                return
            
            # Handle commands
            if text.startswith('/'):
                command_name = text[1:].split()[0].lower()
                await self.run_command(command_name, update, context)
            else:
                # Send unknown command message
                await update.message.reply_text(
                    "❌ Unknown command. Use /help to see available commands."
                )
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def run_command(self, command_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run specific command"""
        try:
            # Try to import and execute command
            module = importlib.import_module(f'handlers.{command_name}')
            handler_func = getattr(module, f'handle_{command_name}')
            
            # Call handler with correct arguments
            await handler_func(update, context, self)
            
        except ModuleNotFoundError:
            await update.message.reply_text(f"❌ Unknown command: /{command_name}")
        except Exception as e:
            error_msg = f"Error executing command '/{command_name}': {str(e)}"
            logger.error(error_msg)
            await update.message.reply_text(f"❌ {error_msg}")
    
    async def handle_next_command(self, command_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wait for user response then run command"""
        user_id = update.effective_user.id
        self.waiting_commands[user_id] = command_name
        await update.message.reply_text(f"📝 Please provide your input...")
    
    def process_update(self, update_data):
        """Process update for webhook"""
        if not self.app:
            self._initialize_app()
            
        async def process():
            update = Update.de_json(update_data, self.app.bot)
            await self.app.process_update(update)
        
        # Run async function in sync context
        asyncio.run(process())

# Global bot instance
bot = SimpleBot()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Bot is running with Webhook',
        'webhook_set': bool(WEBHOOK_URL)
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    try:
        update_data = request.get_json()
        bot.process_update(update_data)
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/set-webhook', methods=['GET'])
def set_webhook():
    """Set webhook URL"""
    try:
        if not WEBHOOK_URL:
            return jsonify({'error': 'WEBHOOK_URL not set'})
        
        # Set webhook using requests
        import requests
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            'url': f"{WEBHOOK_URL}/webhook"
        }
        response = requests.post(url, data=payload)
        
        return jsonify({
            'status': 'Webhook set successfully',
            'telegram_response': response.json()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'bot_initialized': bot.app is not None})

def setup_webhook():
    """Setup webhook on startup"""
    if WEBHOOK_URL:
        try:
            import requests
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
            payload = {
                'url': f"{WEBHOOK_URL}/webhook"
            }
            response = requests.post(url, data=payload)
            logger.info(f"✅ Webhook set: {response.json()}")
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")

if __name__ == '__main__':
    setup_webhook()
    app.run(host='0.0.0.0', port=PORT, debug=False)