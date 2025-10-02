from app import telegram_manager, run_async

def handle(user_info, chat_id, message_text):
    """Handle /fulllogout command - complete logout from all devices"""
    
    if not message_text.startswith('/fulllogout '):
        return """
🚫 <b>Complete Logout (All Devices)</b>

📝 <b>Usage:</b>
<code>/fulllogout phone_number</code>

💡 <b>Example:</b>
<code>/fulllogout 1234567890</code>

⚠️ ⚠️ ⚠️ <b>WARNING:</b> ⚠️ ⚠️ ⚠️
• Logs out from ALL devices
• Terminates ALL active sessions
• You'll need to login again everywhere
• Cannot be undone!

🔄 <b>For bot-only logout:</b>
<code>/logout phone_number</code>

📋 <b>First get phone numbers from:</b> <code>/accounts</code>
"""
    
    phone_number = message_text[12:].strip()  # Remove "/fulllogout "
    user_id = user_info.get('id')
    
    if not phone_number:
        return "❌ <b>Phone number required!</b> Use: <code>/fulllogout phone_number</code>"
    
    # Complete logout using run_async helper
    success, result = run_async(
        telegram_manager.logout_completely(user_id, phone_number)
    )
    
    return result