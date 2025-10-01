def handle_profile(user_info, chat_id, message_text):
    """Handle /profile command - Show Telegram profile"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Import here to avoid circular imports
    from app import telegram_sessions, User
    
    # Check if logged in
    if (str(user_id) not in telegram_sessions or 
        not telegram_sessions[str(user_id)].get('is_authenticated')):
        
        # Check if user has saved session for auto-login
        session_string = User.get_data(user_id, "tg_session")
        
        if session_string:
            return """
🔐 <b>Session Found!</b>

You have a saved Telegram session.

🔄 <b>Auto-login available:</b>
<code>/autologin</code> - Login with saved session

Or start fresh:
<code>/login</code> - New login process
"""
        else:
            return """
❌ <b>Not Logged In</b>

🔐 Please login to Telegram first:

<code>/login</code> - Start login process

💡 You'll need API credentials from:
https://my.telegram.org
"""
    
    tg_user_info = telegram_sessions[str(user_id)].get('user_info', {})
    
    profile_message = f"""
👤 <b>Telegram Profile</b>

✅ <b>Logged in as:</b> {tg_user_info.get('first_name', 'N/A')}

📋 <b>Account Information:</b>
• <b>First Name:</b> {tg_user_info.get('first_name', 'N/A')}
• <b>Last Name:</b> {tg_user_info.get('last_name', 'N/A')}
• <b>Username:</b> @{tg_user_info.get('username', 'N/A')}
• <b>User ID:</b> <code>{tg_user_info.get('id', 'N/A')}</code>
• <b>Phone:</b> <code>{tg_user_info.get('phone', 'N/A')}</code>

🔐 <b>Session Status:</b> Active
📱 <b>Auto-login:</b> Enabled

🔄 <b>Update profile:</b> Re-login if needed
🔓 <b>Logout:</b> <code>/logout</code>
"""
    
    return profile_message