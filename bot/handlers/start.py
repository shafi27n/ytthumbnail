from datetime import datetime
from bot.main import Bot, User

def handle_start(user_info, chat_id, message_text):
    """Handle /start command"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'Friend')
    
    # Save user start time
    User.save_data(user_id, "start_time", datetime.now().isoformat())
    Bot.save_data("total_starts", "1")
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>Auto-Modular Telegram Bot</b>
• Zero configuration needed
• Auto command discovery
• Supabase data storage

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
• <b>First Start:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🚀 <b>Get Started:</b>
Try <code>/help</code> for available commands!
"""

    return welcome_text