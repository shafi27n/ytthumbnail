from telegram import Update
from telegram.ext import ContextTypes

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_core):
    """Handle /help command with HTML formatting"""
    
    help_text = """
🆘 <b>Help Center - Auto Modular System</b>

🤖 <b>About System:</b>
This bot uses <b>fully automatic command discovery</b> with <b>Supabase</b> database.

🔧 <b>Core Features:</b>
• <code>Bot.runCommand("command")</code> - Run specific command
• <code>Bot.handleNextCommand("command")</code> - Wait for user input
• <code>Bot.save_data("var", "value")</code> - Save bot data
• <code>User.save_data("var", "value")</code> - Save user data
• HTTP requests, file uploads, keyboards

💡 <b>Available HTML Formatting:</b>
• <b>Bold</b> - <code>&lt;b&gt;text&lt;/b&gt;</code>
• <i>Italic</i> - <code>&lt;i&gt;text&lt;/i&gt;</code>
• <code>Monospace</code> - <code>&lt;code&gt;text&lt;/code&gt;</code>
• <a href="https://example.com">Link</a> - <code>&lt;a href="url"&gt;text&lt;/a&gt;</code>

🎯 <b>Available Commands:</b>
Use <code>/start</code> to see all loaded commands.

🔧 <b>Developer Features:</b>
• Multi-command files: <code>cmd1|cmd2|cmd3.py</code>
• Auto error handling
• Session management
• Database persistence

⚠️ <b>Important Notes:</b>
• Don't use <>& symbols directly in HTML
• Use HTML entities
• URLs must be properly formatted

📚 <b>Need more help?</b>
Check the project documentation.
    """
    
    await bot_core.send_message(update, help_text)