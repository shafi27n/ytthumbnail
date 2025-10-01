from datetime import datetime

def handle_start(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /start command"""
    
    first_name = user_info.get('first_name', 'Friend')
    user_id = user_info.get('id', 'Unknown')
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>Simple Telegram Bot</b>
Built with Flask + Requests

🚀 <b>Features:</b>
• HTML Formatting
• Photo Sharing  
• HTTP Requests
• User Sessions
• Keyboard Support

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>

🕒 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <b>Try:</b> <code>/help</code> for more commands
    """
    
    return welcome_text
