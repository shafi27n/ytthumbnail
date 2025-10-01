from flask import Flask, request, jsonify
import os
import logging
import importlib
import asyncio
import threading

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
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup basic message handlers"""
        logger.info("✅ Bot handlers setup completed")
    
    async def run_command(self, command_name: str, update, context):
        """Run specific command"""
        try:
            module = importlib.import_module(f'handlers.{command_name}')
            handler_func = getattr(module, f'handle_{command_name}')
            await handler_func(update, context, self)
        except ModuleNotFoundError:
            from telegram import Update
            if isinstance(update, Update):
                await update.message.reply_text(f"❌ Unknown command: /{command_name}")
        except Exception as e:
            logger.error(f"Error in run_command: {e}")
            from telegram import Update
            if isinstance(update, Update):
                await update.message.reply_text(f"❌ Command error: {str(e)}")
    
    async def handle_next_command(self, command_name: str, update, context):
        """Wait for user response then run command"""
        user_id = update.effective_user.id
        self.waiting_commands[user_id] = command_name
        await update.message.reply_text(f"📝 Please provide your input for {command_name}...")
    
    def process_webhook_update(self, update_data):
        """Process webhook update without telegram-ext"""
        try:
            # Basic update processing
            if 'message' in update_data:
                message = update_data['message']
                chat_id = message['chat']['id']
                text = message.get('text', '')
                user_id = message['from']['id']
                
                logger.info(f"📨 Received: {text} from {user_id}")
                
                # Handle waiting commands
                if user_id in self.waiting_commands and text:
                    command = self.waiting_commands[user_id]
                    del self.waiting_commands[user_id]
                    # Execute the waiting command
                    self._execute_command(command, chat_id, user_id, text)
                    return
                
                # Handle regular commands
                if text.startswith('/'):
                    command_name = text[1:].split()[0].lower()
                    self._execute_command(command_name, chat_id, user_id, text)
                else:
                    # Send unknown command message
                    self._send_message(chat_id, "❌ Unknown command. Use /help to see available commands.")
                    
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def _execute_command(self, command_name: str, chat_id: int, user_id: int, text: str):
        """Execute command in background thread"""
        def run_async():
            try:
                # Import and run command
                module = importlib.import_module(f'handlers.{command_name}')
                handler_func = getattr(module, f'handle_{command_name}')
                
                # Create simple context
                class SimpleContext:
                    def __init__(self):
                        self.user_data = {}
                
                class SimpleUpdate:
                    def __init__(self, chat_id, user_id, text):
                        self.effective_chat = type('Chat', (), {'id': chat_id})()
                        self.effective_user = type('User', (), {'id': user_id})()
                        self.message = type('Message', (), {
                            'text': text,
                            'reply_text': self.reply_text
                        })()
                    
                    async def reply_text(self, message_text, parse_mode=None):
                        self._send_message_sync(chat_id, message_text, parse_mode)
                    
                    def _send_message_sync(self, chat_id, text, parse_mode=None):
                        """Send message synchronously"""
                        import requests
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        payload = {
                            'chat_id': chat_id,
                            'text': text
                        }
                        if parse_mode:
                            payload['parse_mode'] = parse_mode
                        
                        try:
                            requests.post(url, json=payload, timeout=10)
                        except Exception as e:
                            logger.error(f"Error sending message: {e}")
                
                # Run the handler
                update = SimpleUpdate(chat_id, user_id, text)
                context = SimpleContext()
                
                # Run async function in thread
                asyncio.run(handler_func(update, context, self))
                
            except ModuleNotFoundError:
                self._send_message(chat_id, f"❌ Unknown command: /{command_name}")
            except Exception as e:
                error_msg = f"❌ Error executing '/{command_name}': {str(e)}"
                logger.error(error_msg)
                self._send_message(chat_id, error_msg)
        
        # Run in background thread
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()
    
    def _send_message(self, chat_id: int, text: str, parse_mode=None):
        """Send message to Telegram"""
        import requests
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

# Global bot instance
bot = SimpleBot()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Bot is running successfully!',
        'webhook_url': WEBHOOK_URL,
        'ready': True
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    try:
        update_data = request.get_json()
        logger.info(f"📨 Webhook received: {update_data}")
        
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
        
        import requests
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
    return jsonify({
        'status': 'healthy',
        'bot': 'ready',
        'timestamp': 'now'
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({'message': 'Bot server is working!'})

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
    logger.info("🚀 Starting Flask bot server...")
    setup_webhook()
    app.run(host='0.0.0.0', port=PORT, debug=False)