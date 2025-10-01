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

def handle_autologin(user_info, chat_id, message_text):
    """Handle /autologin command - Auto login with saved session"""
    
    user_id = user_info.get('id')
    
    # Import here to avoid circular imports
    from app import telegram_sessions, User
    
    # Check if already logged in
    if str(user_id) in telegram_sessions and telegram_sessions[str(user_id)].get('is_authenticated'):
        return "✅ <b>Already logged in!</b> Use <code>/profile</code> to see your info."
    
    # Get saved session data
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