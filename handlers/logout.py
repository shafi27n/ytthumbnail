from app import supabase

def handle(user_info, chat_id, message_text):
    """Handle /logout command - logout from account"""
    
    if not message_text.startswith('/logout '):
        return """
🚪 <b>Logout Account</b>

📝 <b>Usage:</b>
<b>/logout phone_number</b>

💡 <b>Example:</b>
<code>/logout 1234567890</code>

⚠️ <b>This will:</b>
• Remove session from database
• Log you out from this device
• Require login again to use

📋 <b>First get phone numbers from:</b> <b>/accounts</b>
"""
    
    phone_number = message_text[8:].strip()
    user_id = user_info.get('id')
    
    # Get session to deactivate
    session = supabase.get_session_by_phone(user_id, phone_number)
    
    if not session:
        return f"""
❌ <b>Account not found!</b>

Phone: <code>{phone_number}</code>

🔍 <b>Check your accounts:</b> <b>/accounts</b>
"""
    
    # Deactivate session
    success = supabase.deactivate_session(session['id'], user_id)
    
    if success:
        return f"""
✅ <b>Logout Successful</b>

📱 <b>Account:</b> <code>{phone_number}</code>
🔐 <b>Session removed from database</b>

📋 <b>Remaining accounts:</b> <b>/accounts</b>
"""
    else:
        return f"""
❌ <b>Logout Failed</b>

📱 <b>Account:</b> <code>{phone_number}</code>

Please try again or contact support.
"""