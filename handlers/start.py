from telegram import Update
from telegram.ext import ContextTypes

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, bot):
    user = update.effective_user
    
    # Save user data
    bot.db.save_user_data(user.id, 'first_seen', 'now')
    
    text = f"""
👋 Hello {user.first_name}!

🤖 This is a simple webhook bot.

🔧 Available commands:
/start - Start bot
/help - Show help

📝 Usage:
• Use commands normally
• Bot will respond via webhook
    """
    
    await update.message.reply_text(text)
