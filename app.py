from flask import Flask, request, jsonify
import requests
import logging
import os
import importlib
import sys
from datetime import datetime
import uuid

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase Configuration
SUPABASE_URL = 'https://megohojyelqspypejlpo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ29ob2p5ZWxxc3B5cGVqbHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMjQxMDAsImV4cCI6MjA2NzkwMDEwMH0.d3qS8Z0ihWXubYp7kYLsGc0qEpDC1iOdxK9QdfozXWo'

# Global storage
user_sessions = {}
bot_data = {}
command_handlers = {}
next_command_handlers = {}

def generate_id(length=8):
    """Generate unique ID"""
    return str(uuid.uuid4())[:length]

class Bot:
    @staticmethod
    def runCommand(command_name, user_info=None, chat_id=None, message_text=None):
        """Run a specific command immediately - continues to next command"""
        try:
            if command_name.startswith('/'):
                command_name = command_name[1:]  # Remove leading slash
            
            if f"/{command_name}" in command_handlers:
                handler = command_handlers[f"/{command_name}"]
                return handler(user_info, chat_id, message_text or "")
            else:
                return f"❌ Command '{command_name}' not found"
        except Exception as e:
            logger.error(f"Error running command {command_name}: {e}")
            return f"❌ Error executing command: {str(e)}"

    @staticmethod
    def handleNextCommand(command_name, user_info, chat_id):
        """Set up next command handler for user response - waits for input"""
        user_id = user_info.get('id')
        
        if command_name.startswith('/'):
            command_name = command_name[1:]  # Remove leading slash
            
        next_command_handlers[user_id] = {
            'command': command_name,
            'timestamp': datetime.now().isoformat(),
            'user_info': user_info,
            'chat_id': chat_id
        }
        return f"🔄 Waiting for your input for command: {command_name}..."

class SupabaseClient:
    def __init__(self):
        self.base_url = SUPABASE_URL
        self.api_key = SUPABASE_KEY

    async def execute_sql(self, sql):
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

    async def create_user_notes_tables(self):
        """Create tables for user notes system"""
        sql = """
        CREATE TABLE IF NOT EXISTS user_notes (
            id TEXT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            username TEXT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            is_pinned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS note_categories (
            id TEXT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            category_name TEXT NOT NULL,
            color TEXT DEFAULT '#000000',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, category_name)
        );
        
        CREATE TABLE IF NOT EXISTS note_tags (
            id TEXT PRIMARY KEY,
            note_id TEXT NOT NULL REFERENCES user_notes(id) ON DELETE CASCADE,
            tag_name TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        return await self.execute_sql(sql)

    async def save_note(self, user_id, username, title, content, category='general'):
        """Save a new note"""
        try:
            note_id = generate_id(8)
            response = requests.post(
                f"{self.base_url}/rest/v1/user_notes",
                method='POST',
                headers={
                    'apikey': self.api_key,
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'Prefer': 'return=representation'
                },
                json={
                    'id': note_id,
                    'user_id': user_id,
                    'username': username,
                    'title': title,
                    'content': content,
                    'category': category,
                    'updated_at': datetime.now().isoformat()
                }
            )
            
            if not response.ok:
                logger.error(f"Save note error: {response.status} {response.text}")
                return None
                
            result = response.json()
            return result[0] if result else {'id': note_id}
            
        except Exception as e:
            logger.error(f"Error saving note: {e}")
            return None

    async def get_user_notes(self, user_id, page=1, limit=10, category=None):
        """Get user notes with pagination"""
        try:
            url = f"{self.base_url}/rest/v1/user_notes?user_id=eq.{user_id}&order=created_at.desc&limit={limit}&offset={(page-1)*limit}"
            if category and category != 'all':
                url += f"&category=eq.{category}"
                
            response = requests.get(
                url,
                headers={
                    'apikey': self.api_key,
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            if not response.ok:
                logger.error(f"Get notes error: {response.status} {response.text}")
                return []
                
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting notes: {e}")
            return []

    async def get_note_by_id(self, note_id):
        """Get specific note by ID"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/user_notes?id=eq.{note_id}",
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
            logger.error(f"Error getting note: {e}")
            return None

    async def delete_note(self, note_id, user_id):
        """Delete a note"""
        try:
            response = requests.delete(
                f"{self.base_url}/rest/v1/user_notes?id=eq.{note_id}&user_id=eq.{user_id}",
                headers={
                    'apikey': self.api_key,
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            return response.ok
            
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return False

    async def update_note(self, note_id, user_id, title=None, content=None, category=None):
        """Update a note"""
        try:
            update_data = {'updated_at': datetime.now().isoformat()}
            if title: update_data['title'] = title
            if content: update_data['content'] = content
            if category: update_data['category'] = category
            
            response = requests.patch(
                f"{self.base_url}/rest/v1/user_notes?id=eq.{note_id}&user_id=eq.{user_id}",
                headers={
                    'apikey': self.api_key,
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                json=update_data
            )
            
            return response.ok
            
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            return False

    async def get_categories(self, user_id):
        """Get user's categories"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/note_categories?user_id=eq.{user_id}",
                headers={
                    'apikey': self.api_key,
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            if not response.ok:
                return []
                
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

    async def create_category(self, user_id, category_name, color='#000000'):
        """Create a new category"""
        try:
            category_id = generate_id(6)
            response = requests.post(
                f"{self.base_url}/rest/v1/note_categories",
                headers={
                    'apikey': self.api_key,
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'Prefer': 'resolution=merge-duplicates'
                },
                json={
                    'id': category_id,
                    'user_id': user_id,
                    'category_name': category_name,
                    'color': color
                }
            )
            
            return response.ok
            
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return False

# Global Supabase client
supabase = SupabaseClient()

class User:
    @staticmethod
    def save_note(user_id, username, title, content, category='general'):
        """Save user note"""
        return supabase.save_note(user_id, username, title, content, category)

    @staticmethod
    def get_notes(user_id, page=1, limit=10, category=None):
        """Get user notes"""
        return supabase.get_user_notes(user_id, page, limit, category)

    @staticmethod
    def get_note(note_id):
        """Get specific note"""
        return supabase.get_note_by_id(note_id)

    @staticmethod
    def delete_note(note_id, user_id):
        """Delete note"""
        return supabase.delete_note(note_id, user_id)

    @staticmethod
    def update_note(note_id, user_id, **kwargs):
        """Update note"""
        return supabase.update_note(note_id, user_id, **kwargs)

    @staticmethod
    def get_categories(user_id):
        """Get user categories"""
        return supabase.get_categories(user_id)

    @staticmethod
    def create_category(user_id, category_name, color='#000000'):
        """Create category"""
        return supabase.create_category(user_id, category_name, color)

def auto_discover_handlers():
    """Automatically discover all handler modules - filename as command"""
    handlers = {}
    
    try:
        handlers_dir = 'handlers'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        handlers_path = os.path.join(current_dir, handlers_dir)
        
        logger.info(f"🔍 Looking for handlers in: {handlers_path}")
        
        if os.path.exists(handlers_path):
            for filename in os.listdir(handlers_path):
                if filename.endswith('.py') and filename != '__init__.py':
                    command_name = filename[:-3]  # Remove .py
                    
                    logger.info(f"📁 Found handler file: {filename} -> /{command_name}")
                    
                    try:
                        # Use importlib to import module
                        spec = importlib.util.spec_from_file_location(
                            command_name, 
                            os.path.join(handlers_path, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Use the main function (handle function)
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

# Create tables on startup
@app.before_first_request
def setup_tables():
    try:
        import asyncio
        asyncio.run(supabase.create_user_notes_tables())
        logger.info("✅ User notes tables setup completed")
    except Exception as e:
        logger.error(f"❌ Table setup error: {e}")

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
                'status': '✅ Bot is running with NOTES SYSTEM',
                'available_commands': list(command_handlers.keys()),
                'total_commands': len(command_handlers),
                'active_sessions': len(next_command_handlers),
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
                
                # Check for next command handler first (waits for user input)
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
        'active_sessions': len(next_command_handlers),
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting bot on port {port} with {len(command_handlers)} commands")
    app.run(host='0.0.0.0', port=port, debug=False)