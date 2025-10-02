from app import telegram_manager, run_async, Bot

def handle(user_info, chat_id, message_text):
    """Handle /login command - login to telegram account"""
    
    if message_text == "/login":
        # Start login process - wait for phone number
        return Bot.handleNextCommand(
            "login", 
            user_info, 
            chat_id,
            """
📱 <b>Telegram Login</b>

🔐 <b>Login to your Telegram account</b>

📝 <b>Please enter your phone number:</b>
<code>1234567890</code>

💡 <b>Examples:</b>
• <code>1234567890</code>
• <code>8801712345678</code>

🌍 <b>Format:</b> Country code + number (without +)

⚠️ <b>Note:</b> 
• You'll receive verification code via Telegram
• If 2FA enabled, password will be needed
• Sessions are stored securely
• Multiple accounts supported
"""
        )
    
    # If we're in next command mode, this is the phone number
    if message_text.isdigit() and len(message_text) >= 8:
        phone_number = message_text
        
        # Start login process
        result = run_async(
            telegram_manager.login_with_phone(phone_number, user_info, chat_id)
        )
        
        return result
    else:
        return """
❌ <b>Invalid phone number!</b>

📱 <b>Please enter a valid phone number:</b>
• Digits only (without +)
• Minimum 8 digits
• Country code + number

💡 <b>Examples:</b>
• <code>1234567890</code>
• <code>8801712345678</code>

<code>/login</code> to try again
"""