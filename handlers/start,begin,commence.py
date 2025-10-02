from datetime import datetime

def main_start_function(user_info, chat_id, message_text):
    """Handle /start, /begin, /commence commands - SAME FILE"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'Friend')
    command_used = message_text.split()[0] if message_text else "/start"
    
    welcome_text = f"""
🎉 <b>Welcome {first_name}!</b>

🚀 <b>Multiple Commands - Same File System</b>
• File: start,begin,commence.py
• Function: main_start_function()
• Commands: /start, /begin, /commence

📊 <b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
• <b>Command Used:</b> <code>{command_used}</code>
• <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>System Working:</b>
✅ Same file handles multiple commands
✅ Different commands, same function
✅ File: start,begin,commence.py

💡 <b>Try these equivalent commands:</b>
• <code>/start</code> - This command
• <code>/begin</code> - Same function
• <code>/commence</code> - Same function

🎯 <b>All three commands run the same code!</b>
"""

    return welcome_text