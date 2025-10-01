from datetime import datetime

def handle_start(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /start command with Supabase demo"""
    
    first_name = user_info.get('first_name', 'Friend')
    user_id = user_info.get('id', 'Unknown')
    
    # Save user start time to Supabase
    bot.user_save_data(user_id, "start_time", datetime.now().isoformat())
    bot.user_save_data(user_id, "first_name", first_name)
    
    # Save bot stats
    bot.bot_save_data("total_starts", 
        int(bot.bot_get_data("total_starts") or 0) + 1
    )
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>Advanced Telegram Bot</b>
With Supabase Database & Error Handling

🚀 <b>Features:</b>
• ✅ HTML Formatting
• ✅ Photo Sharing  
• ✅ HTTP Requests
• ✅ User Sessions
• ✅ Supabase Database
• ✅ Error Handling
• ✅ Keyboard Support

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>

💾 <b>Database:</b> Your data saved to Supabase!

🕒 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <b>Try these commands:</b>
<code>/help</code> - All commands
<code>/data</code> - View your saved data
<code>/savedata</code> - Save custom data
    """
    
    return welcome_text
