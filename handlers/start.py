import asyncio
from database import db

async def handle_start(update, context, bot):
    """Handle /start command"""
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Save user data
    db.save_user_data(user_id, 'started', 'true')
    
    welcome_text = f"""
👋 Welcome to Simple Bot!

🤖 *This bot features:*
• Automatic command loading
• Webhook support  
• Simple setup

🔧 *Available commands:*
/start - Start bot
/help - Show help
/test - Test command

💡 *Your info:*
• User ID: `{user_id}`
• Chat ID: `{chat_id}`

Send /help for more information.
"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')