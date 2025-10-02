import os
from app import Bot

def main(user_info, chat_id, message_text, command_name):
    """Main function for help/assist/support commands"""
    
    if command_name == "help":
        return handle_help(user_info, chat_id, message_text)
    elif command_name == "assist":
        return handle_assist(user_info, chat_id, message_text)
    elif command_name == "support":
        return handle_support(user_info, chat_id, message_text)
    else:
        return handle_help(user_info, chat_id, message_text)

def handle_help(user_info, chat_id, message_text):
    """Handle /help command"""
    
    commands_info = get_commands_info()
    
    return f"""
🆘 <b>Help Center</b> (via /help)

📋 <b>Available Command Groups:</b>
{commands_info}

🔧 <b>Module-Based System:</b>
• Multiple commands per file
• No handle_ function dependency
• Smart command routing

💡 <b>Try these related help commands:</b>
• <b>/assist</b> - Alternative help
• <b>/support</b> - Support help
"""

def handle_assist(user_info, chat_id, message_text):
    """Handle /assist command"""
    
    return """
🤝 <b>Assistance Center</b> (via /assist)

🎯 <b>How to use this bot:</b>
1. Use any command from the available list
2. Multiple commands can come from same file
3. Each command has unique functionality

🔧 <b>Example:</b>
• <b>/start</b>, <b>/begin</b>, <b>/commence</b> - All from same file!
• <b>/ping</b>, <b>/pong</b>, <b>/test</b> - All from same file!

✅ <b>System is working perfectly!</b>
"""

def handle_support(user_info, chat_id, message_text):
    """Handle /support command"""
    
    return """
🛠️ <b>Support Center</b> (via /support)

🔍 <b>Technical Information:</b>
• System: Module-based command handler
• Architecture: Single file, multiple commands
• Routing: Smart command detection

🚀 <b>Available Command Files:</b>
• start,begin,commence.py
• ping,pong,test.py  
• save,store,keep.py
• show,display,view.py
• help,assist,support.py

💡 <b>Each file handles multiple related commands!</b>
"""

def get_commands_info():
    """Get information about all available commands"""
    commands_info = ""
    
    command_groups = {
        "Start Commands": ["/start", "/begin", "/commence"],
        "Test Commands": ["/ping", "/pong", "/test"], 
        "Data Save": ["/save", "/store", "/keep"],
        "Data View": ["/show", "/display", "/view"],
        "Help": ["/help", "/assist", "/support"]
    }
    
    for group, commands in command_groups.items():
        commands_info += f"\n• <b>{group}:</b> " + ", ".join([f"<b>{cmd}</b>" for cmd in commands])
    
    return commands_info