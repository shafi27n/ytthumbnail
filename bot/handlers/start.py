from datetime import datetime

def handle_start(user_info, chat_id, message_text):
    """Handle /start command"""
    
    first_name = user_info.get('first_name', 'Friend')
    user_id = user_info.get('id', 'Unknown')
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🤖 <b>Bot Status:</b> ✅ Running on Render
🔧 <b>Token Source:</b> URL Parameter
🌐 <b>Platform:</b> Render + Flask

📊 <b>Your Information:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
• <b>Name:</b> {first_name}

🚀 <b>Available Commands:</b>
• <code>/help</code> - Show help guide
• <code>/status</code> - System status
• <code>/time</code> - Current time
• <code>/utils</code> - Interactive demo

🕒 <b>Server Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>This bot supports token via URL!</b>
    """
    
    return welcome_text
