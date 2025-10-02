from app import supabase

def handle(user_info, chat_id, message_text):
    """Handle /logout command - logout from account (bot only)"""
    
    if not message_text.startswith('/logout '):
        return """
🚪 <b>Logout Account (Bot Only)</b>

📝 <b>Usage:</b>
<code>/logout phone_number</code>

💡 <b>Example:</b>
<code>/logout 1234567890</code>

⚠️ <b>This will:</b>
• Remove session from this bot only
• Keep you logged in on other devices
• Require login again to use in this bot

🔄 <b>For complete logout (all devices):</b>
<code>/fulllogout phone_number</code>

📋 <b>First get phone numbers from:</b> <code>/accounts</code>
"""
    
    phone_number = message_text[8:].strip()
    user_id = user_info.get('id')
    
    # Get session to deactivate
    session = supabase.get_session_by_phone(user_id, phone_number)
    
    if not session:
        return f"""
❌ <b>Account not found!</b>

📱 <b>Phone:</b> <code>{phone_number}</code>

🔍 <b>Check your accounts:</b> <code>/accounts</code>
"""
    
    # Deactivate session (bot only)
    success = supabase.deactivate_session(session['id'], user_id)
    
    if success:
        return f"""
✅ <b>Logout Successful</b>

📱 <b>Account:</b> <code>{phone_number}</code>
🤖 <b>Removed from this bot only</b>
📱 <b>Still logged in on other devices</b>

📋 <b>Remaining accounts:</b> <code>/accounts</code>
🔐 <b>Login again:</b> <code>/login</code>
"""
    else:
        return f"""
❌ <b>Logout Failed</b>

📱 <b>Account:</b> <code>{phone_number}</code>

Please try again or contact support.
"""