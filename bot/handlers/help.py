import os
import importlib
import pkgutil

def handle_help(user_info, chat_id, message_text):
    """Handle /help command with comprehensive HTML formatting"""
    
    first_name = user_info.get('first_name', 'Friend')
    user_id = user_info.get('id', 'Unknown')
    
    # Get available commands automatically
    available_commands = get_available_commands()
    
    help_text = f"""
🆘 <b>Help Center - Complete Bot Guide</b>

👋 <b>Hello {first_name}!</b> Welcome to your personal assistant bot.

🤖 <b>About This Bot:</b>
This is a <b>fully automatic modular Telegram bot</b> that can handle various types of messages and commands without any manual configuration.

📋 <b>Available Commands ({len(available_commands)}):</b>

{format_commands_list(available_commands)}

<b>🤖 Bot Status: Online & Ready</b>
    """
    
    return help_text

def get_available_commands():
    """Dynamically get available commands from the system"""
    try:
        handlers_package = importlib.import_module('bot.handlers')
        commands = []
        
        for importer, module_name, ispkg in pkgutil.iter_modules(handlers_package.__path__):
            if module_name != '__init__':
                commands.append(f"/{module_name}")
        
        return sorted(commands)
    except Exception as e:
        return ["/start", "/help"]  # Fallback list

def format_commands_list(commands):
    """Format commands list with descriptions"""
    command_descriptions = {
        '/start': 'Start the bot and get welcome message',
        '/help': 'Show this comprehensive help guide', 
        '/stats': 'Show your usage statistics',
        '/settings': 'Configure bot settings (if available)'
    }
    
    formatted_list = []
    for cmd in commands:
        description = command_descriptions.get(cmd, 'Execute this command')
        formatted_list.append(f"• <b>{cmd}</b> - {description}")
    
    return "\n".join(formatted_list)
