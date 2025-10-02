from app import telegram_manager, run_async

def handle(user_info, chat_id, message_text):
    """Handle /use command - switch to specific account"""
    
    if not message_text.startswith('/use '):
        return """
🔀 <b>Switch Account</b>

📝 <b>Usage:</b>
<code>/use phone_number</code>

💡 <b>Example:</b>
<code>/use 1234567890</code>

📋 <b>First get phone numbers from:</b> <code>/accounts</code>
"""
    
    phone_number = message_text[5:].strip()
    
    # Get user accounts to verify
    user_id = user_info.get('id')
    accounts = run_async(
        telegram_manager.get_user_accounts(user_id)
    )
    
    # Check if account exists
    account_exists = any(acc['phone'] == phone_number for acc in accounts)
    
    if not account_exists:
        available_phones = ', '.join([acc['phone'] for acc in accounts]) if accounts else 'None'
        return f"""
❌ <b>Account not found!</b>

📱 <b>Phone:</b> <code>{phone_number}</code>

📋 <b>Your available accounts:</b>
{available_phones}

🔍 <b>Check accounts:</b> <code>/accounts</code>
"""
    
    return f"""
✅ <b>Account Switched</b>

📱 <b>Now using:</b> <code>{phone_number}</code>

📤 <b>Send message with this account:</b>
<code>/send {phone_number} | username | message</code>

💡 <b>Example:</b>
<code>/send {phone_number} | username | Hello from my bot!</code>
"""