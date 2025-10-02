def handle(user_info, chat_id, message_text):
    """Handle /help command - show help menu"""
    
    return """
🔐 <b>Telegram Account Manager - Help</b>

📱 <b>Account Management:</b>
• <b>/login</b> - Login to Telegram account
• <b>/verify</b> - Verify login code  
• <b>/password</b> - Verify 2FA password
• <b>/accounts</b> - Show all logged in accounts
• <b>/use</b> - Switch to specific account
• <b>/logout</b> - Logout from account

📤 <b>Messaging:</b>
• <b>/send</b> - Send message via account

🔧 <b>How to use:</b>

1. <b>First login:</b>
   <code>/login 1234567890</code>

2. <b>Verify code:</b>
   <code>/verify abc123 123456</code>

3. <b>If 2FA enabled:</b>
   <code>/password abc123 mypassword</code>

4. <b>Check accounts:</b>
   <code>/accounts</code>

5. <b>Send message:</b>
   <code>/send 1234567890 | username | Hello!</code>

🔒 <b>Security:</b>
• Sessions stored encrypted in Supabase
• Each user sees only their own accounts
• Automatic logout on session expiry

📝 <b>Note:</b> Replace phone numbers with actual numbers
"""