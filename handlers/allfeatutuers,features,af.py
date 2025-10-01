from datetime import datetime
import requests
from flask import jsonify

# Import from main app
try:
    from app import Bot, User, send_telegram_message, create_keyboard, create_inline_keyboard
except ImportError:
    # Fallback for direct import
    class Bot:
        save_data = staticmethod(lambda x, y: f"✅ Bot data saved: {x} = {y}")
        runCommand = staticmethod(lambda x: f"🔧 Running command: {x}")
        handleNextCommand = staticmethod(lambda x, y, z: "🔄 Waiting for your response...")
    
    class User:
        save_data = staticmethod(lambda x, y, z: f"✅ User data saved: {y} = {z}")
        get_data = staticmethod(lambda x, y: "0")

def handle_allfeatures(user_info, chat_id, message_text):
    """Universal command with all features - can be added to any other command"""
    return all_features_handler(user_info, chat_id, message_text)

def handle_features(user_info, chat_id, message_text):
    """Alias for allfeatures"""
    return all_features_handler(user_info, chat_id, message_text)

def handle_af(user_info, chat_id, message_text):
    """Short alias for allfeatures"""
    return all_features_handler(user_info, chat_id, message_text)

def all_features_handler(user_info, chat_id, message_text, original_command=None):
    """
    UNIVERSAL FEATURE HANDLER - Can be imported and used in any other command
    
    Usage in other commands:
    from handlers.allfeatures,af import all_features_handler
    
    # Add to any command function:
    def handle_yourcommand(user_info, chat_id, message_text):
        # Your existing code
        result = all_features_handler(user_info, chat_id, message_text, "yourcommand")
        return result
    """
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    username = user_info.get('username', '')
    
    # Extract arguments
    args = message_text.split()[1:] if ' ' in message_text else []
    action = args[0] if args else 'show'
    
    # Demo data storage
    Bot.save_data("features_used", "true")
    User.save_data(user_id, "last_feature_use", datetime.now().isoformat())
    
    if action == 'save':
        # Demo data saving
        variable = args[1] if len(args) > 1 else "demo_var"
        value = args[2] if len(args) > 2 else "demo_value"
        
        bot_result = Bot.save_data(variable, value)
        user_result = User.save_data(user_id, variable, value)
        
        return f"""
💾 <b>Data Storage Demo</b>

🤖 <b>Bot Data:</b>
{bot_result}

👤 <b>User Data:</b>
{user_result}

💡 <b>Usage:</b>
<code>/{original_command or 'features'} save variable_name value</code>
"""
    
    elif action == 'keyboard':
        # Demo keyboards
        reply_keyboard = create_keyboard([
            ["📊 Stats", "🛠️ Settings"],
            ["📝 Input", "🎮 Games", "❌ Cancel"]
        ])
        
        inline_keyboard = create_inline_keyboard([
            [{"text": "✅ Approve", "callback_data": "approve_demo"}],
            [{"text": "❌ Deny", "callback_data": "deny_demo"}, 
             {"text": "🔄 Refresh", "callback_data": "refresh_demo"}],
            [{"text": "🌐 Website", "url": "https://example.com"}]
        ])
        
        response_text = f"""
⌨️ <b>Keyboard Demo</b>

🔘 <b>Reply Keyboard:</b>
• Shows as custom keyboard
• User can tap buttons

🔗 <b>Inline Keyboard:</b>
• Appears below message
• Can trigger callbacks
• Can open URLs

💡 <b>Try tapping the buttons below!</b>
"""
        
        message_data = send_telegram_message(chat_id, response_text, parse_mode='HTML')
        message_data['reply_markup'] = inline_keyboard
        return message_data
    
    elif action == 'http':
        # Demo HTTP requests
        try:
            response = requests.get('https://api.github.com', timeout=5)
            status = response.status_code
            http_demo = f"✅ HTTP Request Successful (Status: {status})"
        except Exception as e:
            http_demo = f"❌ HTTP Request Failed: {str(e)}"
        
        return f"""
🌐 <b>HTTP Requests Demo</b>

{http_demo}

💡 <b>Usage in code:</b>
<code>import requests
response = requests.get('https://api.example.com')
print(response.status_code)</code>
"""
    
    elif action == 'next':
        # Demo next command handler
        Bot.handleNextCommand("echo", user_info, chat_id)
        return """
🔄 <b>Next Command Handler Demo</b>

I'm now waiting for your input! 
Send any message and it will be processed by the echo command.

💡 <b>Feature:</b> Bot.handleNextCommand("command_name", user_info, chat_id)
"""
    
    elif action == 'run':
        # Demo run command
        command_to_run = args[1] if len(args) > 1 else "help"
        result = Bot.runCommand(command_to_run)
        return f"""
🔧 <b>Run Command Demo</b>

Executing: <code>{command_to_run}</code>

📝 <b>Result:</b>
{result}

💡 <b>Feature:</b> Bot.runCommand("command_name")
"""
    
    elif action == 'format':
        # Demo text formatting
        return """
🎨 <b>Text Formatting Demo</b>

<b>Bold Text</b>
<i>Italic Text</i>
<code>Monospace Text</code>
<u>Underlined Text</u>

🔗 <a href="https://example.com">Inline Link</a>

💡 <b>Supported Formats:</b>
• HTML formatting
• Markdown (if enabled)
• Custom keyboards
• Inline buttons
"""
    
    else:
        # Show main features menu
        usage_count = int(User.get_data(user_id, "features_usage_count") or 0) + 1
        User.save_data(user_id, "features_usage_count", str(usage_count))
        
        return f"""
🚀 <b>UNIVERSAL FEATURES COMMAND</b>

👋 Welcome <b>{first_name}</b>!
This command demonstrates ALL available features.

📊 <b>Your Stats:</b>
• User ID: <code>{user_id}</code>
• Usage Count: <code>{usage_count}</code>
• Username: @{username if username else 'Not set'}

🛠️ <b>Available Features:</b>

💾 <b>Data Storage</b>
<code>/{original_command or 'features'} save</code> - Save demo data

⌨️ <b>Keyboards</b>  
<code>/{original_command or 'features'} keyboard</code> - Show keyboards

🌐 <b>HTTP Requests</b>
<code>/{original_command or 'features'} http</code> - Test HTTP calls

🔄 <b>Next Command</b>
<code>/{original_command or 'features'} next</code> - Wait for input

🔧 <b>Run Command</b>
<code>/{original_command or 'features'} run help</code> - Run other commands

🎨 <b>Formatting</b>
<code>/{original_command or 'features'} format</code> - Text formatting demo

💡 <b>Integration:</b>
This handler can be added to ANY other command!
"""