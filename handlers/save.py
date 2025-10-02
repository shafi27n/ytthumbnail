from datetime import datetime
import json
from app import Bot, User

def handle(user_info, chat_id, message_text):
    """Handle /save command - waits for user input"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # If no message text provided, wait for user input
    if not message_text or message_text == "/save":
        # Set up next command handler to wait for user input
        return Bot.handleNextCommand("save", user_info, chat_id)
    
    # Extract data after /save command (if provided directly)
    save_data = message_text[6:].strip() if message_text.startswith('/save') else message_text
    
    if not save_data:
        return "❌ <b>No data provided!</b> Please send: <b>/save your data here</b>"
    
    # Get existing data
    existing_data = User.get_data(user_id, "saved_items") or "[]"
    
    try:
        items_list = json.loads(existing_data)
    except:
        items_list = []
    
    # Create new item
    new_item = {
        "id": len(items_list) + 1,
        "text": save_data,
        "timestamp": datetime.now().isoformat()
    }
    
    items_list.append(new_item)
    
    # Save updated list - pass user_info for user table
    result = User.save_data(user_id, "saved_items", json.dumps(items_list), user_info)
    
    return f"""
✅ <b>Data Saved Successfully!</b>

👤 <b>User:</b> {first_name}
🔢 <b>Item ID:</b> #{new_item['id']}
📊 <b>Total Items:</b> {len(items_list)}

📝 <b>Your Data:</b>
<b>{save_data}</b>

🔍 <b>View with:</b> <b>/show</b>

💾 <b>Save Result:</b> {result}
"""