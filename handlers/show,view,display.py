from datetime import datetime
from app import Bot, User

def main(user_info, chat_id, message_text, command_name):
    """Main function for show/display/view commands"""
    
    if command_name == "show":
        return handle_show(user_info, chat_id, message_text)
    elif command_name == "display":
        return handle_display(user_info, chat_id, message_text)
    elif command_name == "view":
        return handle_view(user_info, chat_id, message_text)
    else:
        return "❌ Unknown command"

def handle_show(user_info, chat_id, message_text):
    """Handle /show command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    saved_data = User.get_data(user_id, "saved_data")
    stored_data = User.get_data(user_id, "stored_data")
    kept_data = User.get_data(user_id, "kept_data")
    
    result = f"""
📂 <b>Show Data</b> (via /show)

👤 <b>User:</b> {first_name}
📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💾 <b>Saved Data:</b>
<b>{saved_data if saved_data else 'No data saved'}</b>

🏪 <b>Stored Data:</b>
<b>{stored_data if stored_data else 'No data stored'}</b>

🔒 <b>Kept Data:</b>
<b>{kept_data if kept_data else 'No data kept'}</b>

💡 <b>Save data using:</b>
• <b>/save data</b>
• <b>/store data</b> 
• <b>/keep data</b>
"""
    
    return result

def handle_display(user_info, chat_id, message_text):
    """Handle /display command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    saved_data = User.get_data(user_id, "saved_data")
    
    return f"""
🖥️ <b>Display Data</b> (via /display)

👤 <b>User:</b> {first_name}
📊 <b>Data Preview:</b>

<b>{saved_data if saved_data else 'No data to display'}</b>

🔧 <b>Same data as /show but different presentation!</b>
"""

def handle_view(user_info, chat_id, message_text):
    """Handle /view command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    stored_data = User.get_data(user_id, "stored_data")
    
    return f"""
👀 <b>View Data</b> (via /view)

👤 <b>User:</b> {first_name}
📋 <b>Stored Data:</b>

<b>{stored_data if stored_data else 'No data to view'}</b>

🎯 <b>Another way to view your data from the same module!</b>
"""