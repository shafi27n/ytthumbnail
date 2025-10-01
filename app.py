from flask import Flask, request, jsonify
import os
import logging
from telegram import Update, Bot
from telegram.ext import Application, ContextTypes
from database import BotDatabase

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7628222622:AAEomk7Od-jcKnQMdkmOpejvYYF47BjMAMQ')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')  # Set in Render/Pyroid
PORT = int(os.environ.get('PORT', 10000))

class SimpleBot:
    def __init__(self):
        self.db = BotDatabase()
        self.waiting_commands = {}
        self.app = Application.builder().token(BOT_TOKEN).build()
        
        # Setup message handler
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def run_command(self, command_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run specific command"""
        try:
            module = __import__(f'handlers.{command_name}', fromlist=[''])
            handler = getattr(module, f'handle_{command_name}')
            await handler(update, context, self)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_next_command(self, command_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wait for user response then run command"""
        user_id = update.effective_user.id
        self.waiting_commands[user_id] = command_name
        await update.message.reply_text(f"📝 Please send your input...")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all messages"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Check waiting commands
        if user_id in self.waiting_commands:
            command = self.waiting_commands[user_id]
            del self.waiting_commands[user_id]
            context.user_data['user_response'] = text
            await self.run_command(command, update, context)
            return
        
        # Handle commands
        if text.startswith('/'):
            command_name = text[1:].split(' ')[0].lower()
            await self.run_command(command_name, update, context)
    
    def process_update(self, update_data):
        """Process update synchronously for webhook"""
        update = Update.de_json(update_data, self.app.bot)
        self.app.update_queue.put(update)

# Global bot instance
bot = SimpleBot()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Bot is running with Webhook',
        'bot_username': bot.app.bot.username
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
        
        # Set webhook
        bot.app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
        return jsonify({
            'status': 'Webhook set successfully',
            'webhook_url': f"{WEBHOOK_URL}/webhook"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

def setup_webhook():
    """Setup webhook on startup"""
    if WEBHOOK_URL:
        try:
            webhook_url = f"{WEBHOOK_URL}/webhook"
            bot.app.bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook set: {webhook_url}")
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")

if __name__ == '__main__':
    setup_webhook()
    app.run(host='0.0.0.0', port=PORT, debug=False)
