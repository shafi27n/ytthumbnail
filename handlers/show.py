from datetime import datetime
import json
from app import User

def handle(user_info, chat_id, message_text):
    """Handle /show command - show all saved data"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get saved data
    saved_data = User.get_data(user_id, "saved_items")
    
    if not saved_data:
        return "📭 <b>No saved items found!</b> Use <b>/save your_data</b> to start saving."
    
    try:
        items_list = json.loads(saved_data)
    except Exception as e:
        return f"❌ <b>Error reading your data!</b> {str(e)}"
    
    if not items_list:
        return "📭 <b>Your list is empty!</b>"
    
    # Format all items
    items_text = ""
    for item in items_list:
        time_str = datetime.fromisoformat(item['timestamp']).strftime('%m/%d %H:%M')
        items_text += f"\n#{item['id']} - {time_str}\n<b>{item['text']}</b>\n"
    
    return f"""
📂 <b>Your Saved Items</b>

👤 <b>User:</b> {first_name}
📊 <b>Total Items:</b> {len(items_list)}

{items_text}
🗑️ <b>Delete:</b> <b>/delete ID</b>
"""