from bot.main import command_handlers

def handle_help(user_info, chat_id, message_text):
    """Handle /help command"""
    
    available_commands = "\n".join([f"• <code>{cmd}</code>" for cmd in command_handlers.keys()])
    
    help_text = f"""
🆘 <b>Help Center</b>

📋 <b>Available Commands:</b>
{available_commands}

🔧 <b>System Features:</b>
• Auto Command Discovery
• Multi-command Files (name1,name2,name3.py)
• Bot & User data storage
• Next command handler

💡 <b>Try these:</b>
• <code>/start</code> - Welcome message
• <code>/ping</code> or <code>/pong</code> - Test commands
• <code>/echo Hello</code> - Echo your message
"""

    return help_text