import asyncio
from app import telegram_manager, Bot

def handle(user_info, chat_id, message_text):
    """Handle /login command - login to telegram account"""
    
    if message_text == "/login":
        return """
📱 <b>Telegram Login</b>

🔐 <b>Login to your Telegram account</b>

📝 <b>Usage:</b>
<b>/login phone_number</b>

💡 <b>Examples:</b>
• <code>/login 8801712345678</code>

🌍 <b>Format:</b> Country code + number (without +)

⚠️ <b>Note:</b> 
• You'll receive verification code
• If 2FA enabled, password will be needed
• Sessions are stored securely
"""
    
    # Extract phone number
    phone_number = message_text[7:].strip()  # Remove "/login "
    
    if not phone_number.isdigit():
        return "❌ <b>Invalid phone number!</b> Use digits only (without +)"
    
    # Start login process
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        telegram_manager.login_with_phone(phone_number, user_info, chat_id)
    )
    loop.close()
    
    return result