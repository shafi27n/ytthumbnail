import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

def handle_setup(user_info, chat_id, message_text):
    """Handle /setup command - Setup Telegram API credentials"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract parameters
    parts = message_text.split()
    if len(parts) < 4:
        return """
❌ <b>Invalid Setup Format</b>

📝 <b>Usage:</b>
<code>/setup api_id api_hash phone_number</code>

📋 <b>Example:</b>
<code>/setup 1234567 abcdefgh123456 +8801712345678</code>

🔍 <b>Where to get credentials:</b>
• Visit: https://my.telegram.org
• Create application in "API Development Tools"
"""
    
    api_id = parts[1]
    api_hash = parts[2]
    phone_number = ' '.join(parts[3:])
    
    # Validate API ID (should be integer)
    if not api_id.isdigit():
        return "❌ <b>API_ID must be a number!</b>"
    
    # Import here to avoid circular imports
    from app import telegram_sessions, User
    
    # Store credentials temporarily
    if str(user_id) not in telegram_sessions:
        telegram_sessions[str(user_id)] = {}
    
    telegram_sessions[str(user_id)]['api_id'] = int(api_id)
    telegram_sessions[str(user_id)]['api_hash'] = api_hash
    telegram_sessions[str(user_id)]['phone_number'] = phone_number
    telegram_sessions[str(user_id)]['login_step'] = 'credentials_saved'
    
    # Save to user data for persistence
    User.save_data(user_id, "tg_api_id", api_id)
    User.save_data(user_id, "tg_api_hash", api_hash)
    User.save_data(user_id, "tg_phone", phone_number)
    
    success_message = f"""
✅ <b>Credentials Saved!</b>

📱 <b>Phone:</b> <code>{phone_number}</code>
🆔 <b>API ID:</b> <code>{api_id}</code>
🔑 <b>API Hash:</b> <code>{api_hash}</code>

📲 <b>Next Step:</b>
Now send: <code>/sendcode</code> to receive verification code.

🔒 Your credentials are saved securely.
"""
    
    return success_message