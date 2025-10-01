import asyncio

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

def handle_logout(user_info, chat_id, message_text):
    """Handle /logout command - Logout from Telegram"""
    
    user_id = user_info.get('id')
    
    # Import here to avoid circular imports
    from app import telegram_sessions, User
    
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