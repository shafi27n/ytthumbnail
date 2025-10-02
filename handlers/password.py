import asyncio
from app import telegram_manager

def handle(user_info, chat_id, message_text):
    """Handle /password command - verify 2FA password"""
    
    if not message_text.startswith('/password '):
        return """
🔐 <b>2FA Password</b>

📝 <b>Usage:</b>
<code>/password login_id your_password</code>

💡 <b>Example:</b>
<b>/password abc123 mypassword123</b>

🔍 <b>Get login_id from:</b> /login command
"""
    
    parts = message_text.split()
    if len(parts) < 3:
        return "❌ <b>Invalid format!</b> Use: <code>/password login_id your_password</code>"
    
    login_id = parts[1]
    password = ' '.join(parts[2:])  # Password may contain spaces
    
    # Verify password
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        telegram_manager.verify_password(login_id, password, user_info, chat_id)
    )
    loop.close()
    
    return result