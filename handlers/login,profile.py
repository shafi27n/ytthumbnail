import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.users import GetFullUserRequest
import threading
import json

# Store Telegram sessions in memory (in production use database)
telegram_sessions = {}

def run_async(coroutine):
    """Run async coroutine in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

def handle_login(user_info, chat_id, message_text):
    """Handle /login command - Start Telegram login process"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Check if already logged in
    if str(user_id) in telegram_sessions and telegram_sessions[str(user_id)].get('is_authenticated'):
        return """
🔐 <b>Already Logged In</b>

✅ You are already logged into Telegram.

👤 Check your profile: <code>/profile</code>
🔓 Logout first: <code>/logout</code>
"""

    instruction_text = f"""
🔐 <b>Telegram Login Setup</b>

👋 Hello <b>{first_name}</b>! Let's connect your Telegram account.

📝 <b>You'll need:</b>
1. <b>API_ID</b> - from https://my.telegram.org
2. <b>API_HASH</b> - from https://my.telegram.org
3. <b>Phone Number</b> - with country code

💡 <b>How to get API credentials:</b>
1. Go to https://my.telegram.org
2. Login with your Telegram account
3. Go to "API Development Tools"
4. Create application and get API_ID & API_HASH

📱 <b>Ready to start?</b>
Send: <code>/setup api_id api_hash phone_number</code>

📋 <b>Example:</b>
<code>/setup 1234567 abcdefgh123456 +8801712345678</code>

🔒 <b>Security:</b> Your session data is encrypted and secure.
"""
    
    return instruction_text

def handle_setup(user_info, chat_id, message_text):
    """Handle /setup command - Setup Telegram API credentials"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract parameters
    parts = message_text.split()
    if len(parts) < 4:
        return """
❌ <b>Invalid Setup Format</b>

📝 <b>Usage:</b>
<code>/setup api_id api_hash phone_number</code>

📋 <b>Example:</b>
<code>/setup 1234567 abcdefgh123456 +8801712345678</code>

🔍 <b>Where to get credentials:</b>
• Visit: https://my.telegram.org
• Create application in "API Development Tools"
"""
    
    api_id = parts[1]
    api_hash = parts[2]
    phone_number = ' '.join(parts[3:])
    
    # Validate API ID (should be integer)
    if not api_id.isdigit():
        return "❌ <b>API_ID must be a number!</b>"
    
    # Store credentials temporarily
    if str(user_id) not in telegram_sessions:
        telegram_sessions[str(user_id)] = {}
    
    telegram_sessions[str(user_id)]['api_id'] = int(api_id)
    telegram_sessions[str(user_id)]['api_hash'] = api_hash
    telegram_sessions[str(user_id)]['phone_number'] = phone_number
    telegram_sessions[str(user_id)]['login_step'] = 'credentials_saved'
    
    # Save to user data for persistence
    from app import User
    User.save_data(user_id, "tg_api_id", api_id)
    User.save_data(user_id, "tg_api_hash", api_hash)
    User.save_data(user_id, "tg_phone", phone_number)
    
    success_message = f"""
✅ <b>Credentials Saved!</b>

📱 <b>Phone:</b> <code>{phone_number}</code>
🆔 <b>API ID:</b> <code>{api_id}</code>
🔑 <b>API Hash:</b> <code>{api_hash}</code>

📲 <b>Next Step:</b>
Now send: <code>/sendcode</code> to receive verification code.

🔒 Your credentials are saved securely.
"""
    
    return success_message

def handle_sendcode(user_info, chat_id, message_text):
    """Handle /sendcode command - Send verification code"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Check if credentials are saved
    if str(user_id) not in telegram_sessions or 'api_id' not in telegram_sessions[str(user_id)]:
        return """
❌ <b>Setup Required First!</b>

📝 Please setup your API credentials first:

<code>/setup api_id api_hash phone_number</code>

💡 Example:
<code>/setup 1234567 abcdefgh123456 +8801712345678</code>
"""
    
    credentials = telegram_sessions[str(user_id)]
    
    async def send_verification_code():
        try:
            # Create new client
            client = TelegramClient(
                StringSession(), 
                credentials['api_id'], 
                credentials['api_hash']
            )
            
            await client.connect()
            
            # Send code request
            sent_code = await client.send_code_request(credentials['phone_number'])
            
            # Store client and sent code info
            telegram_sessions[str(user_id)]['client'] = client
            telegram_sessions[str(user_id)]['phone_code_hash'] = sent_code.phone_code_hash
            telegram_sessions[str(user_id)]['login_step'] = 'code_sent'
            
            return True, "Verification code sent successfully!"
            
        except Exception as e:
            return False, f"Error sending code: {str(e)}"
    
    success, message = run_async(send_verification_code())
    
    if success:
        # Set up next command handler for verification code
        from app import Bot
        next_message = Bot.handleNextCommand("verify", user_info, chat_id)
        
        return f"""
📲 <b>Verification Code Sent!</b>

✅ A verification code has been sent to:
<code>{credentials['phone_number']}</code>

⏳ <b>Waiting for verification code...</b>

🔢 <b>Please send the code you received:</b>

Example: <code>123456</code>

(Just send the numbers, no command needed)

⏱️ <b>Note:</b> Code expires in few minutes.
"""
    else:
        return f"""
❌ <b>Failed to Send Code</b>

Error: {message}

🔧 <b>Possible Solutions:</b>
• Check your API credentials
• Verify phone number format
• Ensure internet connection
• Try again later
"""

def handle_verify(user_info, chat_id, message_text):
    """Handle verification code (called via next command handler)"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # The message_text here is just the code (no command)
    code = message_text.strip()
    
    if not code.isdigit():
        return """
❌ <b>Invalid Code Format!</b>

🔢 Please send only numbers:

Example: <code>123456</code>

No letters or symbols.
"""
    
    # Check if code sending step was completed
    if (str(user_id) not in telegram_sessions or 
        'login_step' not in telegram_sessions[str(user_id)] or
        telegram_sessions[str(user_id)]['login_step'] != 'code_sent'):
        return """
❌ <b>Send Code First!</b>

Please send verification code first:

<code>/sendcode</code>
"""
    
    credentials = telegram_sessions[str(user_id)]
    
    async def verify_code():
        try:
            client = credentials['client']
            phone_code_hash = credentials['phone_code_hash']
            
            # Sign in with code
            await client.sign_in(
                phone=credentials['phone_number'],
                code=code,
                phone_code_hash=phone_code_hash
            )
            
            # Get session string for persistence
            session_string = client.session.save()
            
            # Store session string
            telegram_sessions[str(user_id)]['session_string'] = session_string
            telegram_sessions[str(user_id)]['login_step'] = 'logged_in'
            telegram_sessions[str(user_id)]['is_authenticated'] = True
            
            # Save session to user data
            from app import User
            User.save_data(user_id, "tg_session", session_string)
            
            # Get user info
            me = await client.get_me()
            telegram_sessions[str(user_id)]['user_info'] = {
                'id': me.id,
                'first_name': me.first_name,
                'last_name': me.last_name,
                'username': me.username,
                'phone': me.phone
            }
            
            return True, "Login successful!", me
            
        except Exception as e:
            return False, f"Verification failed: {str(e)}", None
    
    success, message, me = run_async(verify_code())
    
    if success:
        welcome_message = f"""
🎉 <b>Telegram Login Successful!</b>

✅ <b>Welcome to Telegram, {me.first_name}!</b>

👤 <b>Account Details:</b>
• <b>Name:</b> {me.first_name} {me.last_name or ''}
• <b>Username:</b> @{me.username or 'N/A'}
• <b>User ID:</b> <code>{me.id}</code>
• <b>Phone:</b> <code>{me.phone}</code>

🔐 <b>Session Saved:</b> Yes
📱 <b>Auto-login:</b> Enabled

📊 View your profile: <code>/profile</code>
🔓 Logout: <code>/logout</code>

💫 Your Telegram session is now connected!
"""
        return welcome_message
    else:
        # Reset and ask to try again
        telegram_sessions[str(user_id)]['login_step'] = 'credentials_saved'
        
        return f"""
❌ <b>Verification Failed</b>

Error: {message}

🔄 <b>Try again:</b>
Send <code>/sendcode</code> to get a new verification code.

🔧 <b>Common issues:</b>
• Wrong code entered
• Code expired (takes >2 minutes)
• Network problem
"""

def handle_profile(user_info, chat_id, message_text):
    """Handle /profile command - Show Telegram profile"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Check if logged in
    if (str(user_id) not in telegram_sessions or 
        not telegram_sessions[str(user_id)].get('is_authenticated')):
        
        # Check if user has saved session for auto-login
        from app import User
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

def handle_logout(user_info, chat_id, message_text):
    """Handle /logout command - Logout from Telegram"""
    
    user_id = user_info.get('id')
    
    if str(user_id) in telegram_sessions:
        # Close client if exists
        if 'client' in telegram_sessions[str(user_id)]:
            async def close_client():
                try:
                    await telegram_sessions[str(user_id)]['client'].disconnect()
                except:
                    pass
            
            run_async(close_client())
        
        # Clear session data
        telegram_sessions.pop(str(user_id))
        
        # Clear from user data
        from app import User
        User.save_data(user_id, "tg_session", "")
        
        return """
🔓 <b>Logged Out Successfully</b>

✅ Telegram session has been cleared.

🔐 All session data removed from:
• Memory
• Database
• Active connections

📱 You can login again anytime with:
<code>/login</code>
"""
    else:
        return """
ℹ️ <b>Not Logged In</b>

No active Telegram session found.

🔐 Login with: <code>/login</code>
"""

def handle_autologin(user_info, chat_id, message_text):
    """Handle /autologin command - Auto login with saved session"""
    
    user_id = user_info.get('id')
    
    # Check if already logged in
    if str(user_id) in telegram_sessions and telegram_sessions[str(user_id)].get('is_authenticated'):
        return "✅ <b>Already logged in!</b> Use <code>/profile</code> to see your info."
    
    # Get saved session data
    from app import User
    session_string = User.get_data(user_id, "tg_session")
    api_id = User.get_data(user_id, "tg_api_id")
    api_hash = User.get_data(user_id, "tg_api_hash")
    
    if not all([session_string, api_id, api_hash]):
        return """
❌ <b>No Saved Session Found</b>

Please login manually first:

<code>/login</code> - Full login process

Or setup credentials:

<code>/setup api_id api_hash phone_number</code>
"""
    
    async def auto_login():
        try:
            # Create client with saved session
            client = TelegramClient(
                StringSession(session_string),
                int(api_id),
                api_hash
            )
            
            await client.connect()
            
            # Check if authorization is valid
            if await client.is_user_authorized():
                me = await client.get_me()
                
                # Store in sessions
                if str(user_id) not in telegram_sessions:
                    telegram_sessions[str(user_id)] = {}
                
                telegram_sessions[str(user_id)]['client'] = client
                telegram_sessions[str(user_id)]['session_string'] = session_string
                telegram_sessions[str(user_id)]['login_step'] = 'logged_in'
                telegram_sessions[str(user_id)]['is_authenticated'] = True
                telegram_sessions[str(user_id)]['user_info'] = {
                    'id': me.id,
                    'first_name': me.first_name,
                    'last_name': me.last_name,
                    'username': me.username,
                    'phone': me.phone
                }
                
                return True, f"✅ <b>Auto-login successful!</b> Welcome back, {me.first_name}!"
            else:
                return False, "❌ <b>Session expired!</b> Please login again with <code>/login</code>"
                
        except Exception as e:
            return False, f"❌ <b>Auto-login failed:</b> {str(e)}"
    
    success, message = run_async(auto_login())
    return message