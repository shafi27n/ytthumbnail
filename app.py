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

# Configuration - Direct environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7628222622:AAEomk7Od-jcKnQMdkmOpejvYYF47BjMAMQ')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
PORT = int(os.environ.get('PORT', 10000))

# Supabase Configuration - Hardcoded
SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

class BotDatabase:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'apikey': self.key
        }
        logger.info("✅ Database initialized")
    
    def save_bot_data(self, key, value):
        """Save bot data using Supabase REST API"""
        try:
            data = {
                'key': str(key),
                'value': str(value)
            }
            response = requests.post(
                f'{self.url}/rest/v1/bot_data',
                headers=self.headers,
                json=data
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error saving bot data: {e}")
            return False
    
    def save_user_data(self, user_id, key, value):
        """Save user data using Supabase REST API"""
        try:
            data = {
                'user_id': str(user_id),
                'key': str(key),
                'value': str(value)
            }
            response = requests.post(
                f'{self.url}/rest/v1/user_data',
                headers=self.headers,
                json=data
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id, key, default=None):
        """Get user data"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/user_data?user_id=eq.{user_id}&key=eq.{key}',
                headers=self.headers
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]['value']
            return default
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return default

class SimpleBot:
    def __init__(self):
        self.waiting_commands = {}
        self.db = BotDatabase()
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
                
                logger.info(f"📨 Message from user_{user_id}: {text}")
                
                # Handle waiting commands
                if user_id in self.waiting_commands and text:
                    command = self.waiting_commands[user_id]
                    del self.waiting_commands[user_id]
                    self._execute_command(command, chat_id, user_id, text, user_response=text)
                    return
                
                # Handle regular commands
                if text.startswith('/'):
                    command_name = text[1:].split()[0].lower()
                    self._execute_command(command_name, chat_id, user_id, text)
                else:
                    self.send_telegram_message(chat_id, "❌ Unknown command. Use /help")
                    
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def _execute_command(self, command_name, chat_id, user_id, original_text, user_response=None):
        """Execute command in background thread"""
        def run_command():
            try:
                module = importlib.import_module(f'handlers.{command_name}')
                handler_func = getattr(module, f'handle_{command_name}')
                
                class SimpleUpdate:
                    def __init__(self, chat_id, user_id, text, bot_instance):
                        self.effective_chat = type('Chat', (), {'id': chat_id})()
                        self.effective_user = type('User', (), {'id': user_id})()
                        self.message = type('Message', (), {
                            'text': text,
                            'reply_text': self.reply_text
                        })()
                        self.bot = bot_instance
                    
                    async def reply_text(self, message_text, parse_mode=None):
                        self.bot.send_telegram_message(self.effective_chat.id, message_text, parse_mode)
                
                class SimpleContext:
                    def __init__(self):
                        self.user_data = {}
                        if user_response:
                            self.user_data['user_response'] = user_response
                
                update = SimpleUpdate(chat_id, user_id, original_text, self)
                context = SimpleContext()
                
                asyncio.run(handler_func(update, context, self))
                
            except ModuleNotFoundError:
                self.send_telegram_message(chat_id, f"❌ Unknown command: /{command_name}")
            except Exception as e:
                logger.error(f"Error in command {command_name}: {e}")
                self.send_telegram_message(chat_id, "❌ Command execution failed")
        
        thread = threading.Thread(target=run_command)
        thread.daemon = True
        thread.start()
    
    async def run_command(self, command_name, update, context):
        """Run another command"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        self._execute_command(command_name, chat_id, user_id, f"/{command_name}")
    
    async def handle_next_command(self, command_name, update, context):
        """Wait for user response"""
        user_id = update.effective_user.id
        self.waiting_commands[user_id] = command_name
        await update.message.reply_text(f"📝 Please provide input...")

# Global bot instance
bot = SimpleBot()

def Bot():
    return bot

def User(user_id):
    return bot.db

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Bot is running!',
        'webhook': bool(WEBHOOK_URL)
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update_data = request.get_json()
        bot.process_webhook_update(update_data)
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/set-webhook', methods=['GET'])
def set_webhook():
    try:
        if not WEBHOOK_URL:
            return jsonify({'error': 'WEBHOOK_URL not set'})
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {'url': f"{WEBHOOK_URL}/webhook"}
        response = requests.post(url, data=payload)
        
        return jsonify({
            'status': 'Webhook set',
            'webhook_url': f"{WEBHOOK_URL}/webhook",
            'response': response.json()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

def setup_webhook():
    if WEBHOOK_URL:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
            payload = {'url': f"{WEBHOOK_URL}/webhook"}
            requests.post(url, data=payload)
            logger.info("✅ Webhook set")
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting bot server...")
    setup_webhook()
    app.run(host='0.0.0.0', port=PORT, debug=False)