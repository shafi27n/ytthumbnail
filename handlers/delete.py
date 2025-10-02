import json
from datetime import datetime
from app import User

def handle(user_info, chat_id, message_text):
    """Handle /delete command"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract ID after /delete command
    delete_input = message_text[8:].strip() if len(message_text) > 8 else ""
    
    if not delete_input:
        return """
🗑️ <b>Delete Saved Item</b>

📝 <b>Usage:</b> 
<b>/delete item_id</b>

💡 <b>Examples:</b>
• <b>/delete 1</b> - Delete item #1
• <b>/delete 3</b> - Delete item #3

🔍 <b>First check items with:</b> <b>/show</b>
"""
    
    # Get item ID
    try:
        item_id = int(delete_input)
    except ValueError:
        return "❌ <b>Invalid ID!</b> Please provide a number like <b>/delete 1</b>"
    
    # Get existing data
    saved_data = User.get_data(user_id, "saved_items")
    
    if not saved_data:
        return "❌ <b>No items to delete!</b> You haven't saved any data yet."
    
    try:
        items_list = json.loads(saved_data)
    except:
        return "❌ <b>Error reading your data!</b>"
    
    # Find and remove item
    item_to_delete = None
    updated_list = []
    
    for item in items_list:
        if item['id'] == item_id:
            item_to_delete = item
        else:
            updated_list.append(item)
    
    if not item_to_delete:
        return f"❌ <b>Item #{item_id} not found!</b> Use <b>/show</b> to see your items."
    
    # Reassign IDs sequentially
    for index, item in enumerate(updated_list, 1):
        item['id'] = index
    
    # Save updated list
    User.save_data(user_id, "saved_items", json.dumps(updated_list))
    
    delete_time = datetime.fromisoformat(item_to_delete['timestamp']).strftime('%Y-%m-%d %H:%M')
    
    return f"""
✅ <b>Item Deleted Successfully!</b>

👤 <b>User:</b> {first_name}
🗑️ <b>Deleted Item ID:</b> #{item_id}
📅 <b>Originally Saved:</b> {delete_time}

📝 <b>Deleted Content:</b>
<b>{item_to_delete['text']}</b>

📊 <b>Remaining Items:</b> {len(updated_list)}
🔍 <b>View updated list:</b> <b>/show</b>
"""