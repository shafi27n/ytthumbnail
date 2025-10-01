from datetime import datetime

def handle_ping(user_info, chat_id, message_text):
    """Handle /ping command"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    return f"""
🏓 <b>Pong!</b>

👋 Hello {first_name}!
🕒 Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✅ Bot is alive and running!

Try <code>/pong</code> for a different response!
"""

def handle_pong(user_info, chat_id, message_text):
    """Handle /pong command"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    return f"""
🎯 <b>Ping!</b>

👋 Hey {first_name}!
🕒 Response Time: {datetime.now().strftime('%H:%M:%S')}
⚡ System is responsive!

This shows multi-command file working!
"""