from datetime import datetime

def delete_data_function(user_info, chat_id, message_text):
    """Handle /delete, /remove, /clear commands - SAME FILE"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    command_used = message_text.split()[0] if message_text else "/delete"
    
    response_text = f"""
🗑️ <b>Data Delete System</b>

🔧 <b>Command Details:</b>
• File: delete,remove,clear.py
• Function: delete_data_function()
• Command Used: <code>{command_used}</code>

👤 <b>User:</b> {first_name}
🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

📝 <b>Usage:</b>
<code>{command_used} item_id</code>

💡 <b>Examples:</b>
• <code>{command_used} 1</code> - Delete item 1
• <code>{command_used} 2</code> - Delete item 2

🎯 <b>Equivalent Commands:</b>
• <code>/delete</code> - Delete data
• <code>/remove</code> - Delete data
• <code>/clear</code> - Delete data

✅ <b>All delete commands work the same way!</b>

🔧 <b>System Proof:</b>
Same file handles: delete, remove, clear
Different commands, identical function
"""
    
    return response_text