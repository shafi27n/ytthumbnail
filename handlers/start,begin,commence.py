from datetime import datetime
from app import Bot

def main(user_info, chat_id, message_text, command_name):
    """Main function that handles all commands from this file"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'Friend')
    
    # Determine which command was called
    if command_name == "start":
        return handle_start(user_info, chat_id, message_text)
    elif command_name == "begin":
        return handle_begin(user_info, chat_id, message_text)
    elif command_name == "commence":
        return handle_commence(user_info, chat_id, message_text)
    else:
        return handle_start(user_info, chat_id, message_text)

def handle_start(user_info, chat_id, message_text):
    """Handle /start command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'Friend')
    
    return f"""
🎉 <b>Welcome {first_name}!</b> (via /start)

🤖 <b>Module-Based Command System</b>
• Single file, multiple commands
• No handle_ function dependency
• Smart command routing

📊 <b>Your Info:</b>
• <b>User ID:</b> <b>{user_id}</b>
• <b>Chat ID:</b> <b>{chat_id}</b>
• <b>Command:</b> <b>/start</b>

🚀 <b>Try these related commands:</b>
• <b>/begin</b> - Alternative start
• <b>/commence</b> - Formal start
"""

def handle_begin(user_info, chat_id, message_text):
    """Handle /begin command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'Friend')
    
    return f"""
🚀 <b>Let's Begin {first_name}!</b> (via /begin)

🎯 <b>Ready to explore?</b>
This is the alternative start command from the same file as /start.

📋 <b>What's different:</b>
• Same file, different function
• Different welcome message
• Same powerful system

💡 <b>Now try:</b> <b>/commence</b> for another variant!
"""

def handle_commence(user_info, chat_id, message_text):
    """Handle /commence command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'Friend')
    
    return f"""
🏁 <b>Commencing Operations!</b> (via /commence)

🛠️ <b>Formal Welcome {first_name}</b>
This is the formal commencement command.

🔧 <b>System Status:</b>
• Module: start,begin,commence.py
• Commands: /start, /begin, /commence
• All from single file

✅ <b>All systems operational!</b>
"""