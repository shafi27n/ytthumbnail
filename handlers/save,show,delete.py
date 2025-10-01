from datetime import datetime
import json

def handle_save(user_info, chat_id, message_text):
    """Handle /save command - Save user data with serial numbers"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract data after /save command
    save_data = message_text[6:].strip() if len(message_text) > 6 else ""
    
    if not save_data:
        instruction_text = """
💾 <b>Save User Data</b>

📝 <b>Usage:</b> 
<code>/save your_data_here</code>

💡 <b>Examples:</b>
• <code>/save My favorite color is blue</code>
• <code>/save Phone: 01712345678</code>
• <code>/save Important note: Meeting tomorrow at 10 AM</code>

🔢 <b>Multiple items will be stored with serial numbers</b>
"""
        return instruction_text
    
    # Get existing data
    from app import User
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
    
    # Save updated list
    result = User.save_data(user_id, "saved_items", json.dumps(items_list))
    
    success_message = f"""
✅ <b>Data Saved Successfully!</b>

👤 <b>User:</b> {first_name}
🔢 <b>Item ID:</b> #{new_item['id']}
📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 <b>Your Saved Data:</b>
<code>{save_data}</code>

📊 <b>Total Items:</b> {len(items_list)}
🔍 <b>View all:</b> <code>/show</code>
"""
    
    return success_message

def handle_show(user_info, chat_id, message_text):
    """Handle /show command - Show all saved data with serial numbers"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get saved data
    from app import User
    saved_data = User.get_data(user_id, "saved_items")
    
    if not saved_data:
        no_data_message = f"""
📭 <b>No Data Found</b>

👤 <b>User:</b> {first_name}
❌ <b>Status:</b> You haven't saved any data yet!

💾 <b>To save data:</b>
<code>/save your_text_here</code>

💡 <b>Example:</b>
<code>/save My important information</code>
"""
        return no_data_message
    
    try:
        items_list = json.loads(saved_data)
    except:
        items_list = []
    
    if not items_list:
        return "📭 <b>No saved items found!</b>"
    
    # Format all items
    items_text = ""
    for item in items_list:
        time_str = datetime.fromisoformat(item['timestamp']).strftime('%m/%d %H:%M')
        items_text += f"\n#{item['id']} - {time_str}\n<code>{item['text']}</code>\n"
    
    data_message = f"""
📂 <b>Your Saved Items</b>

👤 <b>User:</b> {first_name}
📊 <b>Total Items:</b> {len(items_list)}
📅 <b>Retrieved:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{items_text}
🗑️ <b>Delete item:</b> <code>/delete ID</code>
💡 <b>Example:</b> <code>/delete 1</code>
"""
    
    return data_message

def handle_delete(user_info, chat_id, message_text):
    """Handle /delete command - Delete specific item by ID"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract ID after /delete command
    delete_input = message_text[8:].strip() if len(message_text) > 8 else ""
    
    if not delete_input:
        instruction_text = """
🗑️ <b>Delete Saved Item</b>

📝 <b>Usage:</b> 
<code>/delete item_id</code>

💡 <b>Examples:</b>
• <code>/delete 1</code> - Delete item #1
• <code>/delete 3</code> - Delete item #3

🔍 <b>First check items with:</b> <code>/show</code>
"""
        return instruction_text
    
    # Get item ID
    try:
        item_id = int(delete_input)
    except ValueError:
        return "❌ <b>Invalid ID!</b> Please provide a number like <code>/delete 1</code>"
    
    # Get existing data
    from app import User
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
        return f"❌ <b>Item #{item_id} not found!</b> Use <code>/show</code> to see your items."
    
    # Reassign IDs sequentially
    for index, item in enumerate(updated_list, 1):
        item['id'] = index
    
    # Save updated list
    User.save_data(user_id, "saved_items", json.dumps(updated_list))
    
    delete_time = datetime.fromisoformat(item_to_delete['timestamp']).strftime('%Y-%m-%d %H:%M')
    
    success_message = f"""
✅ <b>Item Deleted Successfully!</b>

👤 <b>User:</b> {first_name}
🗑️ <b>Deleted Item ID:</b> #{item_id}
📅 <b>Originally Saved:</b> {delete_time}

📝 <b>Deleted Content:</b>
<code>{item_to_delete['text']}</code>

📊 <b>Remaining Items:</b> {len(updated_list)}
🔍 <b>View updated list:</b> <code>/show</code>
"""
    
    return success_message

def handle_mydata(user_info, chat_id, message_text):
    """Handle /mydata command - Alias for /show"""
    return handle_show(user_info, chat_id, message_text)

def handle_clear(user_info, chat_id, message_text):
    """Handle /clear command - Delete all saved data"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get existing data to show what will be deleted
    from app import User
    saved_data = User.get_data(user_id, "saved_items")
    
    if not saved_data:
        return "❌ <b>No data to clear!</b> You haven't saved any items yet."
    
    try:
        items_list = json.loads(saved_data)
        total_items = len(items_list)
    except:
        total_items = 0
    
    # Clear all data
    User.save_data(user_id, "saved_items", "[]")
    
    return f"""
🗑️ <b>All Data Cleared!</b>

👤 <b>User:</b> {first_name}
✅ <b>Deleted Items:</b> {total_items}
📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💾 <b>Storage is now empty</b>
💡 <b>Start fresh with:</b> <code>/save your_new_data</code>
"""
