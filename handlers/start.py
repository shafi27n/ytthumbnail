from datetime import datetime
from app import Bot

def handle(user_info, chat_id, message_text):
    """Handle /start command"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'Friend')
    
    # Example of Bot.runCommand - runs immediately
    help_result = Bot.runCommand("help", user_info, chat_id)
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>File-Based Command System</b>
• Each file = One command
• Filename = Command name
• Advanced command chaining

📊 <b>Your Info:</b>
• <b>User ID:</b> <b>{user_id}</b>
• <b>Chat ID:</b> <b>{chat_id}</b>
• <b>First Start:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🚀 <b>Auto-executed Help:</b>
{help_result}
"""

    return welcome_text