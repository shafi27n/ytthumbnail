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

⚡ <b>System Features:</b>
• <b>Auto-Command Discovery</b> - New commands load automatically
• <b>Multi-Media Support</b> - Photos, videos, documents, etc.
• <b>HTML Formatting</b> - Beautiful formatted responses
• <b>File Upload System</b> - Forward to channels with links
• <b>Zero Configuration</b> - Just add command files

📋 <b>Available Commands ({len(available_commands)}):</b>

{format_commands_list(available_commands)}

📁 <b>Media Upload System:</b>

📸 <b>How to upload files:</b>
1. Use <code>/upload</code> command for instructions
2. Send any file (photo, document, video, audio, voice)
3. Bot auto-forwards to @refffrrr channel
4. Get direct download link instantly

🔄 <b>Supported File Types:</b>
• <b>Photos</b> (JPEG, PNG, GIF) - Send as photo
• <b>Documents</b> (PDF, ZIP, DOC, etc.) - Any file type
• <b>Videos</b> (MP4, AVI, MOV) - Video files
• <b>Audio</b> (MP3, WAV) - Music files
• <b>Voice Messages</b> - Voice recordings

🔧 <b>For Developers:</b>

<code>How to add new commands:</code>
1. Create <code>command_name.py</code> in handlers folder
2. Write <code>handle_command_name(user_info, chat_id, message_text)</code> function
3. Return HTML formatted string
4. <b>Done!</b> Command auto-loads on restart

<code>Special Media Handlers:</code>
• <code>handle_photo(message)</code> - For photo messages
• <code>handle_document(message)</code> - For document messages
• <code>handle_video(message)</code> - For video messages
• <code>handle_audio(message)</code> - For audio messages
• <code>handle_voice(message)</code> - For voice messages

👤 <b>Your Information:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
• <b>Name:</b> {first_name}

⚠️ <b>Important Notes:</b>
• Use <code>&lt;b&gt;bold&lt;/b&gt;</code> for bold text
• Use <code>&lt;i&gt;italic&lt;/i&gt;</code> for emphasis
• Use <code>&lt;code&gt;monospace&lt;/code&gt;</code> for code
• File size limit: <b>20MB</b> (Telegram restriction)

📞 <b>Need More Help?</b>
If you encounter any issues or need new features:
1. Check available commands with <code>/help</code>
2. Try the <code>/upload</code> command for file sharing
3. Contact the system administrator

🚀 <b>Quick Start:</b>
Begin with <code>/start</code> for basic introduction or <code>/upload</code> to share files immediately!

<code>🤖 Bot Status: Online & Ready</code>
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
        return ["/start", "/help", "/upload"]  # Fallback list

def format_commands_list(commands):
    """Format commands list with descriptions"""
    command_descriptions = {
        '/start': 'Start the bot and get welcome message',
        '/help': 'Show this comprehensive help guide', 
        '/upload': 'Upload files to channel and get sharing links',
        '/time': 'Show current server time and date',
        '/profile': 'Display your profile information',
        '/stats': 'Show your usage statistics',
        '/settings': 'Configure bot settings (if available)'
    }
    
    formatted_list = []
    for cmd in commands:
        description = command_descriptions.get(cmd, 'Execute this command')
        formatted_list.append(f"• <code>{cmd}</code> - {description}")
    
    return "\n".join(formatted_list)
