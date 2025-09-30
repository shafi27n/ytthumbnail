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
<code>No configuration needed</code> for new commands.

🚀 <b>Features:</b>
• Auto command discovery
• Zero configuration needed
• Easy extension
• HTML formatted messages

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
{f'• <b>Username:</b> @{username}' if username else '• <b>Username:</b> Not set'}

💡 <b>How to add commands:</b>
1. Create <code>command_name.py</code> in handlers folder
2. Write <code>handle_command_name</code> function
3. <b>Done!</b> Command auto-loads!

🕒 <b>Server Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>Get started:</b> <code>/help</code>
    """
    
    return welcome_text
