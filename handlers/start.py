def handle(user_info, chat_id, message_text):
    """Handle /start command - welcome message and bot introduction"""
    
    first_name = user_info.get('first_name', 'User')
    
    return f"""
👋 <b>Welcome {first_name}!</b>

🔐 <b>Telegram Account Manager Bot</b>

Manage multiple Telegram accounts from one place with advanced features!

🚀 <b>Main Features:</b>
• 📱 <b>Multi-Account Login</b> - Login multiple Telegram accounts
• 🔐 <b>Secure Sessions</b> - Store sessions safely in database  
• 📤 <b>Smart Messaging</b> - Send messages from any account
• 🔄 <b>Easy Switching</b> - Switch between accounts instantly
• 🛡️ <b>2FA Support</b> - Full two-factor authentication support

📋 <b>Quick Start:</b>

1. <b>Login to your first account:</b>
   <code>/login 1234567890</code>

2. <b>Verify the code you receive:</b>
   <code>/verify login_id 123456</code>

3. <b>Check your accounts:</b>
   <code>/accounts</code>

4. <b>Send a message:</b>
   <code>/send 1234567890 | username | Hello!</code>

🔧 <b>Available Commands:</b>

<b>Account Management:</b>
• /login - Login to Telegram account
• /verify - Verify login code
• /password - Verify 2FA password  
• /accounts - Show all accounts
• /use - Switch to account
• /logout - Logout from account

<b>Messaging:</b>
• /send - Send message via account

<b>Help:</b>
• /help - Detailed help guide

🔒 <b>Security Notes:</b>
• Your sessions are stored encrypted in Supabase
• Each user can only access their own accounts
• Automatic session management
• Secure logout available

💡 <b>Need help?</b> Use <code>/help</code> for detailed instructions.

Let's get started! Try <code>/login your_phone_number</code>
"""