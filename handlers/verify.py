import asyncio
from app import telegram_manager

def handle(user_info, chat_id, message_text):
    """Handle /verify command - verify login code"""
    
    if not message_text.startswith('/verify '):
        return """
🔢 <b>Verification Code</b>

📝 <b>Usage:</b>
<code>/verify login_id code</code>

💡 <b>Example:</b>
<b>/verify abc123 123456</b>

🔍 <b>Get login_id from:</b> /login command
"""
    
    parts = message_text.split()
    if len(parts) < 3:
        return "❌ <b>Invalid format!</b> Use: <code>/verify login_id code</code>"
    
    login_id = parts[1]
    code = parts[2]
    
    if not code.isdigit():
        return "❌ <b>Invalid code!</b> Code must be digits only."
    
    # Verify code
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        telegram_manager.verify_code(login_id, code, user_info, chat_id)
    )
    loop.close()
    
    return result