def handle_help(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /help command"""
    
    help_text = """
🆘 <b>Help Center</b>

🤖 <b>Available Commands:</b>
• <code>/start</code> - Welcome & setup
• <code>/help</code> - This help message  
• <code>/time</code> - Current time
• <code>/photo</code> - Send demo photo
• <code>/http</code> - Test HTTP request
• <code>/data</code> - View your saved data
• <code>/savedata</code> - Save custom data
• <code>/interactive</code> - Interactive demo

🔧 <b>Bot Features:</b>
• HTML text formatting
• Image sharing
• Web requests (GET/POST)
• User data storage (Supabase)
• Error handling
• Interactive keyboards

💾 <b>Database Features:</b>
• <code>User.saveData("key", "value")</code>
• <code>Bot.saveData("key", "value")</code>
• Data persists across sessions
• Secure cloud storage

🚀 <b>Enjoy using the bot!</b>
    """
    
    return help_text
