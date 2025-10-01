from flask import Flask, request, jsonify
import os
import logging
import importlib
import requests
import threading
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
        logger.info("✅ Bot initialized")
    
    def send_telegram_message(self, chat_id, text, parse_mode=None):
        """Send message via Telegram Bot API"""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text
            }
            if parse_mode:
                payload['parse_mode'] = parse_mode
            
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def process_webhook_update(self, update_data):
        """Process webhook update"""
        try:
            if 'message' in update_data:
                message = update_data['message']
                chat_id = message['chat']['id']
                text = message.get('text', '').strip()
                user_id = message['from']['id']
                first_name = message['from'].get('first_name', 'User')
                
                logger.info(f"📨 Message from {first_name}: {text}")
                
                # Handle waiting commands
                if user_id in self.waiting_commands and text:
                    command = self.waiting_commands[user_id]
                    del self.waiting_commands[user_id]
                    
                    # Execute waiting command with user response
                    self._execute_command(command, chat_id, user_id, text, user_response=text)
                    return
                
                # Handle regular commands
                if text.startswith('/'):
                    command_name = text[1:].split()[0].lower()
                    self._execute_command(command_name, chat_id, user_id, text)
                else:
                    # Unknown command
                    self.send_telegram_message(
                        chat_id, 
                        "❌ Unknown command. Use /help to see available commands."
                    )
                    
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def _execute_command(self, command_name, chat_id, user_id, original_text, user_response=None):
        """Execute command in background thread"""
        def run_command():
            try:
                # Import the command module
                module = importlib.import_module(f'handlers.{command_name}')
                handler_func = getattr(module, f'handle_{command_name}')
                
                # Create simple update and context objects
                class SimpleUpdate:
                    def __init__(self, chat_id, user_id, text, bot_instance):
                        self.effective_chat = type('Chat', (), {'id': chat_id})()
                        self.effective_user = type('User', (), {
                            'id': user_id,
                            'first_name': 'User'
                        })()
                        self.message = type('Message', (), {
                            'text': text,
                            'chat': type('Chat', (), {'id': chat_id})(),
                            'reply_text': self.reply_text
                        })()
                        self.bot = bot_instance
                    
                    async def reply_text(self, message_text, parse_mode=None):
                        # Convert async to sync for message sending
                        self.bot.send_telegram_message(
                            self.effective_chat.id, 
                            message_text, 
                            parse_mode
                        )
                
                class SimpleContext:
                    def __init__(self):
                        self.user_data = {}
                        if user_response:
                            self.user_data['user_response'] = user_response
                
                # Create instances
                update = SimpleUpdate(chat_id, user_id, original_text, self)
                context = SimpleContext()
                
                # Run the handler
                asyncio.run(handler_func(update, context, self))
                
            except ModuleNotFoundError:
                self.send_telegram_message(chat_id, f"❌ Unknown command: /{command_name}")
            except Exception as e:
                error_msg = f"❌ Error in /{command_name}: {str(e)}"
                logger.error(error_msg)
                self.send_telegram_message(chat_id, error_msg)
        
        # Run in background thread
        thread = threading.Thread(target=run_command)
        thread.daemon = True
        thread.start()
    
    def run_command(self, command_name, update, context):
        """Run another command - for use inside handlers"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        text = f"/{command_name}"
        self._execute_command(command_name, chat_id, user_id, text)
    
    async def handle_next_command(self, command_name, update, context):
        """Wait for user response then run command"""
        user_id = update.effective_user.id
        self.waiting_commands[user_id] = command_name
        
        await update.message.reply_text(
            f"📝 Please provide your input for {command_name}..."
        )

# Global bot instance
bot = SimpleBot()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Bot is running successfully!',
        'webhook_set': bool(WEBHOOK_URL),
        'ready': True
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    try:
        update_data = request.get_json()
        logger.info(f"📨 Webhook received")
        
        # Process the update
        bot.process_webhook_update(update_data)
        
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
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            'url': f"{WEBHOOK_URL}/webhook"
        }
        response = requests.post(url, data=payload)
        
        result = response.json()
        
        return jsonify({
            'status': 'Webhook set successfully',
            'webhook_url': f"{WEBHOOK_URL}/webhook",
            'telegram_response': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'bot': 'ready'})

def setup_webhook():
    """Setup webhook on startup"""
    if WEBHOOK_URL:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
            payload = {
                'url': f"{WEBHOOK_URL}/webhook"
            }
            response = requests.post(url, data=payload)
            logger.info(f"✅ Webhook set: {response.json()}")
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting Flask bot server...")
    setup_webhook()
    app.run(host='0.0.0.0', port=PORT, debug=False)