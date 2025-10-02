from datetime import datetime

def help_system_function(user_info, chat_id, message_text):
    """Handle /help, /assist, /support commands - SAME FILE"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    command_used = message_text.split()[0] if message_text else "/help"
    
    # Access global variables directly instead of class attributes
    from app import next_command_handlers, command_queue
    
    active_sessions = len(next_command_handlers)
    queued_commands = sum(len(q) for q in command_queue.values())
    
    help_text = f"""
🆘 <b>Help System</b>

🔧 <b>Command Details:</b>
• File: help,assist,support.py
• Function: help_system_function()
• Command Used: <b>{command_used}</b>

👤 <b>User:</b> {first_name}
🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

📋 <b>Available Command Groups:</b>

• <b>Start Commands:</b>
  <b>/start</b>, <b>/begin</b>, <b>/commence</b>

• <b>Test Commands:</b>
  <b>/ping</b>, <b>/pong</b>, <b>/test</b>

• <b>Save Commands:</b>
  <b>/save</b>, <b>/store</b>, <b>/keep</b>

• <b>Show Commands:</b>
  <b>/show</b>, <b>/display</b>, <b>/view</b>

• <b>Help Commands:</b>
  <b>/help</b>, <b>/assist</b>, <b>/support</b>

• <b>Delete Commands:</b>
  <b>/delete</b>, <b>/remove</b>, <b>/clear</b>

🎯 <b>Multiple Commands System:</b>
✅ Each group has multiple commands
✅ All commands in group use same file
✅ Different commands, same functionality

📊 <b>System Status:</b>
• Active Sessions: {active_sessions}
• Queued Commands: {queued_commands}

💡 <b>Try equivalent commands in each group!</b>
"""
    
    return help_text