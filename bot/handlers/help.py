def handle_help(user_info, chat_id, message_text):
    """Handle /help command"""
    
    help_text = """
🆘 <b>Help Guide</b>

🤖 <b>About This Bot:</b>
This is a fully automatic Telegram bot deployed on Render with URL token support.

📚 <b>Available Commands:</b>
• <code>/start</code> - Welcome message and user info
• <code>/help</code> - This help guide  
• <code>/status</code> - System status information
• <code>/time</code> - Current server time
• <code>/utils</code> - Utilities menu

🔧 <b>Technical Features:</b>
• Token via URL parameter (?token=YOUR_TOKEN)
• HTML message formatting
• Auto command discovery

💡 <b>URL Token Usage:</b>
<code>https://yourapp.onrender.com/?token=YOUR_BOT_TOKEN</code>

⚠️ <b>Note:</b> Token can also be set via BOT_TOKEN environment variable.

🔗 <b>Need Help?</b> Contact the developer.
    """
    
    return help_text
