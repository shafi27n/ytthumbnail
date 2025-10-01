from datetime import datetime

def handle_start(user_info, chat_id, message_text, bot_manager=None, **kwargs):
    """Handle /start command with enhanced features"""
    
    first_name = user_info.get('first_name', 'Friend')
    username = user_info.get('username', '')
    user_id = user_info.get('id', 'Unknown')
    
    # Create welcome keyboard
    welcome_keyboard = [
        [
            bot_manager.create_keyboard_button("🚀 Features Demo"),
            bot_manager.create_keyboard_button("📚 Help")
        ],
        [
            bot_manager.create_keyboard_button("🕒 Time"),
            bot_manager.create_keyboard_button("🔧 Advanced")
        ]
    ]
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>About This Bot:</b>
I'm an <b>ENHANCED AUTOMATIC</b> modular Telegram bot!
<code>Zero configuration</code> • <code>Multi-command files</code> • <code>Full API support</code>

🚀 <b>Enhanced Features:</b>
• ✅ Auto command discovery
• ✅ Multi-command files (name1|name2|name3.py)
• ✅ HTML/Markdown formatting
• ✅ Media sharing (photos, videos, documents)
• ✅ Inline & Reply keyboards
• ✅ HTTP requests (GET/POST)
• ✅ User sessions & data storage
• ✅ Message editing/deleting
• ✅ Pending response handling

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
{f'• <b>Username:</b> @{username}' if username else '• <b>Username:</b> Not set'}

💡 <b>Quick Start:</b>
Use the keyboard below or try:
<code>/advanced</code> - All features demo
<code>/help</code> - Detailed guide

🕒 <b>Server Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    # Send message with welcome keyboard
    result = bot_manager.send_message(
        chat_id=chat_id,
        text=welcome_text,
        reply_markup=bot_manager.create_reply_keyboard(welcome_keyboard)
    )
    
    return "Welcome message sent with interactive keyboard!"
