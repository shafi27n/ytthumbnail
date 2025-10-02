import asyncio
from app import telegram_manager

def handle(user_info, chat_id, message_text):
    """Handle /use command - switch to specific account"""
    
    if not message_text.startswith('/use '):
        return """
🔀 <b>Switch Account</b>

📝 <b>Usage:</b>
<code>/use phone_number</code>

💡 <b>Example:</b>
<b>/use 1234567890</b>

📋 <b>First get phone numbers from:</b> <b>/accounts</b>
"""
    
    phone_number = message_text[5:].strip()
    
    # Get user accounts to verify
    user_id = user_info.get('id')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    accounts = loop.run_until_complete(
        telegram_manager.get_user_accounts(user_id)
    )
    loop.close()
    
    # Check if account exists
    account_exists = any(acc['phone'] == phone_number for acc in accounts)
    
    if not account_exists:
        return f"""
❌ <b>Account not found!</b>

Phone: <code>{phone_number}</code>

📋 <b>Your available accounts:</b>
{', '.join([acc['phone'] for acc in accounts]) if accounts else 'None'}

🔍 <b>Check accounts:</b> <b>/accounts</b>
"""
    
    return f"""
✅ <b>Account Switched</b>

📱 <b>Now using:</b> <code>{phone_number}</code>

📤 <b>Send message with this account:</b>
<code>/send {phone_number} | username | message</code>

💡 <b>Example:</b>
<code>/send {phone_number} | username | Hello from my bot!</code>
"""