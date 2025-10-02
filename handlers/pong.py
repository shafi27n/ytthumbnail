from datetime import datetime

def handle(user_info, chat_id, message_text):
    """Handle /pong command"""
    
    first_name = user_info.get('first_name', 'User')
    
    return f"""
🎯 <b>Pong Response</b>

👋 Hey {first_name}!
🕒 Response Time: {datetime.now().strftime('%H:%M:%S')}
⚡ This is the pong response!

🏓 Try <b>/ping</b> to see command chaining!
"""