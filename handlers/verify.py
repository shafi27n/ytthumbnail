from app import telegram_manager, run_async, Bot

def handle(user_info, chat_id, message_text):
    """Handle /verify command - verify login code"""
    
    if not message_text.startswith('/verify '):
        return """
🔢 <b>Verification Code</b>

📝 <b>Usage:</b>
<code>/verify login_id code</code>

💡 <b>Example:</b>
<code>/verify abc123 123456</code>

🔍 <b>Get login_id from:</b> /login command
"""
    
    parts = message_text.split()
    if len(parts) < 3:
        return "❌ <b>Invalid format!</b> Use: <code>/verify login_id code</code>"
    
    login_id = parts[1]
    code = parts[2]
    
    if not code.isdigit():
        return "❌ <b>Invalid code!</b> Code must be digits only."
    
    # Verify code using run_async helper
    result = run_async(
        telegram_manager.verify_code(login_id, code, user_info, chat_id)
    )
    
    return result