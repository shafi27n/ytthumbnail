from datetime import datetime
from app import Bot

def handle(user_info, chat_id, message_text):
    """Handle /ping command"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Example of running another command immediately
    pong_result = Bot.runCommand("pong", user_info, chat_id)
    
    return f"""
🏓 <b>Ping Command</b>

👋 Hello {first_name}!
🕒 Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 <b>Auto-executed Pong:</b>
{pong_result}

✅ <b>Bot.runCommand</b> runs immediately!
"""