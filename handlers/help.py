import os
import importlib

# Dynamically get available commands
def get_available_commands():
    commands = []
    handlers_dir = 'handlers'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    handlers_path = os.path.join(current_dir, '..', handlers_dir)
    
    if os.path.exists(handlers_path):
        for filename in os.listdir(handlers_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                command_names = module_name.split(',')
                commands.extend([f"/{cmd}" for cmd in command_names])
    
    return commands

def handle_help(user_info, chat_id, message_text):
    """Handle /help command"""
    
    available_commands = get_available_commands()
    commands_text = "\n".join([f"• <code>{cmd}</code>" for cmd in available_commands])
    
    help_text = f"""
🆘 <b>Help Center - FIXED VERSION</b>

📋 <b>Available Commands:</b>
{commands_text}

🔧 <b>System Features:</b>
• Auto Command Discovery - NOW WORKING!
• Multi-command Files (name1,name2,name3.py)
• Bot & User data storage
• Next command handler

💡 <b>Try these:</b>
• <code>/start</code> - Welcome message
• <code>/ping</code> or <code>/pong</code> - Test commands
• <code>/echo Hello</code> - Echo your message

✅ <b>Status:</b> All commands should work now!
"""

    return help_text