import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

def handle_sendcode(user_info, chat_id, message_text):
    """Handle /sendcode command - Send verification code"""
    
    user_id = user_info.get('id')
    
    # Import here to avoid circular imports
    from app import telegram_sessions, Bot
    
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