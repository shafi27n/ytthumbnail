from datetime import datetime

def help_system_function(user_info, chat_id, message_text):
    """Handle /help, /assist, /support commands - SAME FILE"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    command_used = message_text.split()[0] if message_text else "/help"
    
    help_text = f"""
🆘 <b>Help System</b>

🔧 <b>Command Details:</b>
• File: help,assist,support.py
• Function: help_system_function()
• Command Used: <code>{command_used}</code>

👤 <b>User:</b> {first_name}
🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

📋 <b>Available Command Groups:</b>

• <b>Start Commands:</b>
  <code>/start</code>, <code>/begin</code>, <code>/commence</code>

• <b>Test Commands:</b>
  <code>/ping</code>, <code>/pong</code>, <code>/test</code>

• <b>Save Commands:</b>
  <code>/save</code>, <code>/store</code>, <code>/keep</code>

• <b>Show Commands:</b>
  <code>/show</code>, <code>/display</code>, <code>/view</code>

• <b>Help Commands:</b>
  <code>/help</code>, <code>/assist</code>, <code>/support</code>

🎯 <b>Multiple Commands System:</b>
✅ Each group has multiple commands
✅ All commands in group use same file
✅ Different commands, same functionality

💡 <b>Try equivalent commands in each group!</b>
"""
    
    return help_text