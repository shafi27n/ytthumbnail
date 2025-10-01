import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

def handle_login(user_info, chat_id, message_text):
    """Handle /login command - Start Telegram login process"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Import here to avoid circular imports
    from app import telegram_sessions
    
    # Check if already logged in
    if str(user_id) in telegram_sessions and telegram_sessions[str(user_id)].get('is_authenticated'):
        return """
🔐 <b>Already Logged In</b>

✅ You are already logged into Telegram.

👤 Check your profile: <code>/profile</code>
🔓 Logout first: <code>/logout</code>
"""

    instruction_text = f"""
🔐 <b>Telegram Login Setup</b>

👋 Hello <b>{first_name}</b>! Let's connect your Telegram account.

📝 <b>You'll need:</b>
1. <b>API_ID</b> - from https://my.telegram.org
2. <b>API_HASH</b> - from https://my.telegram.org
3. <b>Phone Number</b> - with country code

🔒 <b>2FA Support:</b>
• If your account has two-step verification
• You'll be asked for password after code
• Both phone code and password supported

💡 <b>How to get API credentials:</b>
1. Go to https://my.telegram.org
2. Login with your Telegram account
3. Go to "API Development Tools"
4. Create application and get API_ID & API_HASH

📱 <b>Ready to start?</b>
Send: <code>/setup api_id api_hash phone_number</code>

📋 <b>Example:</b>
<code>/setup 1234567 abcdefgh123456 +8801712345678</code>

🔒 <b>Security:</b> Your session data is encrypted and secure.
"""
    
    return instruction_text