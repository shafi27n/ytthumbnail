from datetime import datetime

def handle_save(user_info, chat_id, message_text):
    """Handle /save command - Save user data"""
    
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

🔒 <b>Your data will be saved securely!</b>
"""
        return instruction_text
    
    # Save the data using User class
    from app import User
    result = User.save_data(user_id, "saved_text", save_data)
    
    success_message = f"""
✅ <b>Data Saved Successfully!</b>

👤 <b>User:</b> {first_name}
📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 <b>Your Saved Data:</b>
<code>{save_data}</code>

📊 <b>Storage Info:</b>
• User ID: <code>{user_id}</code>
• Chat ID: <code>{chat_id}</code>

🔍 View your data with: <code>/show</code>
"""
    
    return success_message

def handle_show(user_info, chat_id, message_text):
    """Handle /show command - Show saved user data"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get saved data using User class
    from app import User
    saved_data = User.get_data(user_id, "saved_text")
    
    if saved_data is None:
        no_data_message = f"""
📭 <b>No Data Found</b>

👤 <b>User:</b> {first_name}
❌ <b>Status:</b> You haven't saved any data yet!

💾 <b>To save data:</b>
<code>/save your_text_here</code>

💡 <b>Example:</b>
<code>/save My important information</code>

🔒 Your data will be saved securely and privately!
"""
        return no_data_message
    
    # Show the saved data
    data_message = f"""
📂 <b>Your Saved Data</b>

👤 <b>User:</b> {first_name}
🆔 <b>User ID:</b> <code>{user_id}</code>
📅 <b>Retrieved:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 <b>Saved Content:</b>
<code>{saved_data}</code>

💾 <b>Storage:</b> Supabase Database
🔒 <b>Privacy:</b> Only you can see your data

🔄 <b>Update your data:</b>
<code>/save new_data_here</code>
"""
    
    return data_message

def handle_mydata(user_info, chat_id, message_text):
    """Handle /mydata command - Alias for /show"""
    return handle_show(user_info, chat_id, message_text)