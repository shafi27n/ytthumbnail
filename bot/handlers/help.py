def handle_help(user_info, chat_id, message_text):
    """Handle /help command with HTML formatting"""
    
    help_text = """
🆘 <b>Help Center - Auto Modular System</b>

🤖 <b>About System:</b>
This bot uses <b>fully automatic command discovery</b> system.

🔧 <b>How it works:</b>
• Add new command files in <code>handlers/</code> folder
• System auto-detects and loads them
• <b>No manual registration needed</b>

💡 <b>Available HTML Formatting:</b>
• <b>Bold</b> - <code>&lt;b&gt;text&lt;/b&gt;</code>
• <i>Italic</i> - <code>&lt;i&gt;text&lt;/i&gt;</code>
• <code>Monospace</code> - <code>&lt;code&gt;text&lt;/code&gt;</code>
• <a href="https://example.com">Link</a> - <code>&lt;a href="url"&gt;text&lt;/a&gt;</code>

⚠️ <b>Important Notes:</b>
• Don't use <>& symbols directly
• Use HTML entities like <code>&amp;lt;</code> for <
• URLs must be properly formatted

📚 <b>Need more help?</b>
Contact the developer for assistance.

🔧 <b>Current commands:</b> Check <code>/start</code> for available commands.
    """
    
    return help_text
