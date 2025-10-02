import os
from app import Bot

def handle(user_info, chat_id, message_text):
    """Handle /help command"""
    
    from app import command_handlers
    
    available_commands = list(command_handlers.keys())
    commands_text = "\n".join([f"• <b>{cmd}</b>" for cmd in available_commands])
    
    help_text = f"""
🆘 <b>Help Center - FILE-BASED SYSTEM</b>

📋 <b>Available Commands:</b>
{commands_text}

🔧 <b>Command Types:</b>
• <b>Instant:</b> Bot.runCommand("help") - runs immediately
• <b>Wait for Input:</b> Bot.handleNextCommand("save") - waits for user

💡 <b>Try these:</b>
• <b>/start</b> - Welcome (auto-runs help)
• <b>/ping</b> - Test response
• <b>/save</b> - Save data (waits for input)
• <b>/setup</b> - Setup database

⚡ <b>Each file is one command!</b>
"""

    return help_text