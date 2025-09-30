from datetime import datetime

def handle_start(user_info, chat_id, message_text):
    """Handle /start command with HTML formatting"""
    
    first_name = user_info.get('first_name', 'Friend')
    username = user_info.get('username', '')
    user_id = user_info.get('id', 'Unknown')
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>About Me:</b>
I'm a <b>FULLY AUTOMATIC</b> modular Telegram bot!
<b>No configuration needed</b> for new commands.

📊 <b>Your Info:</b>
• <b>User ID:</b> <b>{user_id}</b>
• <b>Chat ID:</b> <b>{chat_id}</b>
{f'• <b>Username:</b> @{username}' if username else '• <b>Username:</b> Not set'}

🕒 <b>Server Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>Get started:</b> <b>/help</b>
    """
    
    return welcome_text
