from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_core):
    """Handle /start command with HTML formatting"""
    
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Save user data
    bot_core.db.save_user_data(user.id, 'first_seen', datetime.now().isoformat())
    bot_core.db.save_user_data(user.id, 'username', user.username or '')
    bot_core.db.save_user_data(user.id, 'full_name', user.full_name)
    
    # Update bot stats
    total_users = bot_core.db.get_bot_data('total_users', 0) + 1
    bot_core.db.save_bot_data('total_users', total_users)
    
    welcome_text = f"""
🎉 <b>Welcome {user.first_name}!</b>

🤖 <b>About Me:</b>
I'm a <b>FULLY AUTOMATIC</b> modular Telegram bot with <b>Supabase</b> integration!
<code>No configuration needed</code> for new commands.

🚀 <b>Advanced Features:</b>
• Auto command discovery
• Supabase database storage  
• HTML/Markdown formatting
• Inline keyboards & buttons
• File uploads (photos/videos)
• HTTP API calls
• User sessions
• Error handling

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user.id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
• <b>Username:</b> @{user.username or 'Not set'}
• <b>First Seen:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <b>How to add commands:</b>
1. Create <code>command_name.py</code> in handlers folder
2. Write <code>handle_command_name</code> function  
3. <b>Done!</b> Command auto-loads!

🔧 <b>Get started:</b> <code>/help</code>
    """
    
    await bot_core.send_message(update, welcome_text)