from datetime import datetime
from bot.core.bot_manager import UserManager

def handle_start(user_info, chat_id, message_text, bot_manager):
    """Handle /start command with HTML formatting"""
    
    first_name = user_info.get('first_name', 'Friend')
    username = user_info.get('username', '')
    user_id = user_info.get('id', 'Unknown')
    
    # Initialize user manager and save some data
    user_manager = UserManager(user_id)
    user_manager.save_data('first_seen', datetime.now().isoformat())
    user_manager.save_data('username', username or 'Not set')
    
    # Save bot-level data
    bot_manager.save_data('total_starts', str(int(bot_manager.get_data('total_starts') or 0) + 1))
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>About Me:</b>
I'm a <b>FULLY AUTOMATIC SUPER BOT</b> with advanced features!
<code>No configuration needed</code> for new commands.

🚀 <b>Advanced Features:</b>
• Auto command discovery
• Supabase database integration  
• User data management
• Bot data management
• Next command handling
• Multi-command files
• Full Telegram API support

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
{f'• <b>Username:</b> @{username}' if username else '• <b>Username:</b> Not set'}

💡 <b>How to add commands:</b>
1. Create <code>command_name.py</code> in handlers folder
2. Write <code>handle_command_name</code> function
3. Accept <code>bot_manager</code> parameter
4. <b>Done!</b> Command auto-loads!

🕒 <b>Server Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>Get started:</b> <code>/help</code>
    """
    
    return welcome_text
