import asyncio
from telethon import TelegramClient

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

def handle_verify(user_info, chat_id, message_text):
    """Handle verification code (called via next command handler)"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # The message_text here is just the code (no command)
    code = message_text.strip()
    
    if not code:
        return "❌ <b>Empty code!</b> Please send the verification code."
    
    # Import here to avoid circular imports
    from app import telegram_sessions, User, Bot
    
    # Check if code sending step was completed
    if (str(user_id) not in telegram_sessions or 
        'login_step' not in telegram_sessions[str(user_id)]):
        return """
❌ <b>Send Code First!</b>

Please send verification code first:

<code>/sendcode</code>
"""
    
    credentials = telegram_sessions[str(user_id)]
    login_step = credentials.get('login_step')
    
    async def verify_code():
        try:
            client = credentials['client']
            
            if login_step == 'code_sent':
                # First step: Verify phone code
                phone_code_hash = credentials['phone_code_hash']
                
                try:
                    # Try to sign in with code
                    await client.sign_in(
                        phone=credentials['phone_number'],
                        code=code,
                        phone_code_hash=phone_code_hash
                    )
                except Exception as e:
                    # If 2FA required, it will raise error
                    if "two-steps" in str(e).lower() or "password" in str(e).lower():
                        # 2FA required - ask for password
                        telegram_sessions[str(user_id)]['login_step'] = 'need_password'
                        return 'need_password', "2FA password required", None
                    else:
                        # Other error
                        return 'error', f"Verification failed: {str(e)}", None
                
                # If no 2FA, login successful
                return await finalize_login(client, user_id)
                
            elif login_step == 'need_password':
                # Second step: Verify 2FA password
                try:
                    await client.sign_in(password=code)
                    return await finalize_login(client, user_id)
                except Exception as e:
                    return 'error', f"Password verification failed: {str(e)}", None
            else:
                return 'error', "Invalid login step. Please start over with /login", None
            
        except Exception as e:
            return 'error', f"Verification failed: {str(e)}", None
    
    async def finalize_login(client, user_id):
        """Finalize login after successful verification"""
        # Get session string for persistence
        session_string = client.session.save()
        
        # Store session string
        telegram_sessions[str(user_id)]['session_string'] = session_string
        telegram_sessions[str(user_id)]['login_step'] = 'logged_in'
        telegram_sessions[str(user_id)]['is_authenticated'] = True
        
        # Save session to user data
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
        
        return 'success', "Login successful!", me
    
    success, message, me = run_async(verify_code())
    
    if success == 'need_password':
        # Set up next command handler for password
        Bot.handleNextCommand("verify", user_info, chat_id)
        
        return f"""
🔐 <b>Two-Step Verification Required</b>

✅ Phone code verified successfully!
🔒 Account has 2FA protection.

📝 <b>Please enter your 2FA password:</b>

(Your Telegram cloud password)

💡 <b>Note:</b> This is not your phone lock password!
"""
    
    elif success == 'success':
        welcome_message = f"""
🎉 <b>Telegram Login Successful!</b>

✅ <b>Welcome to Telegram, {me.first_name}!</b>

👤 <b>Account Details:</b>
• <b>Name:</b> {me.first_name} {me.last_name or ''}
• <b>Username:</b> @{me.username or 'N/A'}
• <b>User ID:</b> <code>{me.id}</code>
• <b>Phone:</b> <code>{me.phone}</code>
• <b>2FA Protection:</b> ✅ Enabled

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
        
        error_response = f"""
❌ <b>Verification Failed</b>

Error: {message}

"""
        
        if "invalid code" in message.lower():
            error_response += """
🔢 <b>Invalid Code:</b>
• Check the code and try again
• Codes are usually 6 digits
• They expire after 5 minutes
"""
        elif "flood" in message.lower():
            error_response += """
⏳ <b>Flood Wait:</b>
• Too many attempts
• Please wait a few minutes
• Try again later
"""
        else:
            error_response += """
🔄 <b>Try again:</b>
Send <code>/sendcode</code> to get a new verification code.
"""
        
        return error_response