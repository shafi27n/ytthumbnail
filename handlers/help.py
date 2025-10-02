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

📤 <b>Messaging:</b>
• <b>/send</b> - Send message via account

🚪 <b>Logout Options:</b>
• <b>/logout</b> - Logout from bot only
• <b>/fulllogout</b> - Complete logout (all devices)

🔧 <b>How to use:</b>

1. <b>First login:</b>
   <code>/login</code>
   Then enter your phone number

2. <b>Verify code:</b>
   You'll receive code via Telegram
   <code>/verify login_id 123456</code>

3. <b>If 2FA enabled:</b>
   <code>/password login_id mypassword</code>

4. <b>Check accounts:</b>
   <code>/accounts</code>

5. <b>Send message:</b>
   <code>/send 1234567890 | username | Hello!</code>

🔒 <b>Security:</b>
• Sessions stored encrypted in Supabase
• Each user sees only their own accounts
• Two logout options for flexibility

⚠️ <b>Important Notes:</b>
• Use <code>/logout</code> to remove from bot only
• Use <code>/fulllogout</code> to logout from all devices
• Multiple accounts supported simultaneously
• Proper 2FA handling for secure login

📝 <b>Support:</b>
If you face any issues, restart the login process with <code>/login</code>
"""