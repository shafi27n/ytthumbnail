from telegram import Update
from telegram.ext import ContextTypes
from database import db

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, bot):
    user = update.effective_user
    
    # Save user data
    db.save_user_data(user.id, 'first_name', user.first_name)
    if user.username:
        db.save_user_data(user.id, 'username', user.username)
    
    text = f"""
👋 Hello *{user.first_name}*!

🤖 *Welcome to Simple Bot*

🔧 *Available Commands:*
/start - Start bot
/help - Show help

💡 *How to use:*
Just send any command starting with /

📊 *Your Info:*
• User ID: `{user.id}`
• Chat ID: `{update.effective_chat.id}`
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')