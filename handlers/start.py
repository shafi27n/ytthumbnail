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
• 🚪 <b>Flexible Logout</b> - Bot-only or complete logout

📋 <b>Quick Start:</b>

1. <b>Login to your first account:</b>
   <code>/login</code>

2. <b>Follow the steps:</b>
   • Enter phone number
   • Verify code from Telegram
   • Enter 2FA password (if enabled)

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

<b>Messaging:</b>
• /send - Send message via account

<b>Logout:</b>
• /logout - Logout from bot only
• /fulllogout - Complete logout (all devices)

<b>Help:</b>
• /help - Detailed help guide

🔒 <b>Security Notes:</b>
• Your sessions are stored encrypted in Supabase
• Each user can only access their own accounts
• Automatic session management
• Flexible logout options

💡 <b>Need help?</b> Use <code>/help</code> for detailed instructions.

Let's get started! Try <code>/login</code>
"""