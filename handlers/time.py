from datetime import datetime

def handle_time(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /time command"""
    
    current_time = datetime.now()
    user_id = user_info.get('id')
    
    # Save last time check to Supabase
    bot.user_save_data(user_id, "last_time_check", current_time.isoformat())
    
    time_text = f"""
🕒 <b>Current Time</b>

📅 <b>Date:</b> {current_time.strftime('%Y-%m-%d')}
⏰ <b>Time:</b> {current_time.strftime('%H:%M:%S')}
🌐 <b>Timezone:</b> Server Time

📊 <b>Formats:</b>
• ISO: <code>{current_time.isoformat()}</code>
• Full: {current_time.strftime('%A, %B %d, %Y at %I:%M %p')}

💡 <b>Timestamp:</b> <code>{int(current_time.timestamp())}</code>

💾 <b>Saved to your profile!</b>
    """
    
    return time_text
