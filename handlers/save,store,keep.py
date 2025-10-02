from datetime import datetime
import json
from app import Bot, User

def main(user_info, chat_id, message_text, command_name):
    """Main function for save/store/keep commands"""
    
    if command_name == "save":
        return handle_save(user_info, chat_id, message_text)
    elif command_name == "store":
        return handle_store(user_info, chat_id, message_text)
    elif command_name == "keep":
        return handle_keep(user_info, chat_id, message_text)
    else:
        return "❌ Unknown command"

def handle_save(user_info, chat_id, message_text):
    """Handle /save command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract data after /save command
    save_data = message_text[6:].strip() if len(message_text) > 6 else ""
    
    if not save_data:
        return """
💾 <b>Save Data</b> (via /save)

📝 <b>Usage:</b> 
<b>/save your_data_here</b>

💡 <b>Examples:</b>
• <b>/save My important note</b>
• <b>/save Phone: 01712345678</b>

🔧 <b>Related commands:</b>
• <b>/store</b> - Alternative save
• <b>/keep</b> - Another variant
"""
    
    # Save the data
    result = User.save_data(user_id, "saved_data", save_data)
    
    return f"""
✅ <b>Data Saved</b> (via /save)

👤 <b>User:</b> {first_name}
📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📝 <b>Data:</b> <b>{save_data}</b>

💾 <b>Status:</b> {result}
"""

def handle_store(user_info, chat_id, message_text):
    """Handle /store command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract data after /store command
    store_data = message_text[7:].strip() if len(message_text) > 7 else ""
    
    if not store_data:
        return """
🏪 <b>Store Data</b> (via /store)

📝 <b>Usage:</b> 
<b>/store your_data_here</b>

💡 <b>Examples:</b>
• <b>/store My secret info</b>
• <b>/store Email: user@example.com</b>

🔧 <b>Same functionality as /save but different command!</b>
"""
    
    # Store the data
    result = User.save_data(user_id, "stored_data", store_data)
    
    return f"""
🏪 <b>Data Stored</b> (via /store)

👤 <b>User:</b> {first_name}
📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📦 <b>Data:</b> <b>{store_data}</b>

💾 <b>Status:</b> {result}
"""

def handle_keep(user_info, chat_id, message_text):
    """Handle /keep command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract data after /keep command
    keep_data = message_text[6:].strip() if len(message_text) > 6 else ""
    
    if not keep_data:
        return """
🔒 <b>Keep Data</b> (via /keep)

📝 <b>Usage:</b> 
<b>/keep your_data_here</b>

💡 <b>Examples:</b>
• <b>/keep Important reminder</b>
• <b>/keep Password: 123456</b>

🔧 <b>Another variant of save command from same file!</b>
"""
    
    # Keep the data
    result = User.save_data(user_id, "kept_data", keep_data)
    
    return f"""
🔒 <b>Data Kept</b> (via /keep)

👤 <b>User:</b> {first_name}
📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🗃️ <b>Data:</b> <b>{keep_data}</b>

💾 <b>Status:</b> {result}
"""