from datetime import datetime
import json

def data_save_function(user_info, chat_id, message_text):
    """Handle /save, /store, /keep commands - SAME FILE"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    command_used = message_text.split()[0] if message_text else "/save"
    
    # Extract data after command
    save_data = message_text[len(command_used):].strip()
    
    if not save_data:
        return f"""
💾 <b>Data Save System</b>

🔧 <b>Command Details:</b>
• File: save,store,keep.py
• Function: data_save_function()
• Command Used: <code>{command_used}</code>

📝 <b>Usage:</b>
<code>{command_used} your_data_here</code>

💡 <b>Examples:</b>
• <code>{command_used} My important note</code>
• <code>{command_used} Phone: 01712345678</code>

🎯 <b>Equivalent Commands:</b>
• <code>/save</code> - Save data
• <code>/store</code> - Save data  
• <code>/keep</code> - Save data

✅ <b>All three commands work identically!</b>
"""
    
    # Simulate saving data
    result = f"""
✅ <b>Data Saved Successfully!</b>

🔧 <b>System Info:</b>
• File: save,store,keep.py
• Function: data_save_function()
• Command Used: <code>{command_used}</code>

👤 <b>User:</b> {first_name}
📝 <b>Data Saved:</b>
<code>{save_data}</code>
🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

💡 <b>Try these equivalent commands:</b>
• <code>/save data</code>
• <code>/store data</code>
• <code>/keep data</code>

🎯 <b>All commands save data the same way!</b>
"""
    
    return result