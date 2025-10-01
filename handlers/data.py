def handle_data(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /data command - View saved user data"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get all user data from Supabase
    user_data = bot.user_get_all_data(user_id)
    
    if not user_data:
        return f"""
📊 <b>Your Saved Data</b>

👤 <b>User:</b> {first_name}
🆔 <b>ID:</b> <code>{user_id}</code>

💾 <b>Database Status:</b> No data found

💡 <b>To save data:</b>
Use <code>/savedata</code> command
Or interact with other commands
        """
    
    # Format user data
    data_lines = []
    for item in user_data:
        data_lines.append(f"• <b>{item['variable']}:</b> {item['value']}")
    
    data_text = "\n".join(data_lines)
    
    # Get bot stats
    total_starts = bot.bot_get_data("total_starts") or 0
    total_photos = bot.bot_get_data("total_photos_sent") or 0
    
    return f"""
📊 <b>Your Saved Data</b>

👤 <b>User:</b> {first_name}
🆔 <b>ID:</b> <code>{user_id}</code>
📦 <b>Total Items:</b> {len(user_data)}

💾 <b>Your Data:</b>
{data_text}

🤖 <b>Bot Statistics:</b>
• Total Starts: {total_starts}
• Photos Sent: {total_photos}

🔧 <b>Manage Data:</b>
<code>/savedata</code> - Add new data
<code>/cleardata</code> - Clear your data
    """

def handle_savedata(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /savedata command - Save custom data"""
    
    # Check if this is the initial command or a response
    if not kwargs.get('is_pending'):
        bot.handle_next_command(chat_id, "process_savedata", user_info)
        return """
💾 <b>Save Custom Data</b>

📝 <b>Step 1:</b> What data do you want to save?

💡 <b>Format:</b> 
<code>variable_name = value</code>

📋 <b>Example:</b>
<code>favorite_color = blue</code>

🔧 <b>Now type your data in the format above:</b>
        """
    
    # Process the user's data input
    try:
        if '=' not in message_text:
            return "❌ Invalid format. Please use: <code>variable_name = value</code>"
        
        variable, value = message_text.split('=', 1)
        variable = variable.strip()
        value = value.strip()
        
        if not variable or not value:
            return "❌ Both variable name and value are required."
        
        # Save to Supabase
        success = bot.user_save_data(user_info['id'], variable, value)
        
        if success:
            return f"""
✅ <b>Data Saved Successfully!</b>

📦 <b>Variable:</b> <code>{variable}</code>
💾 <b>Value:</b> <code>{value}</code>
👤 <b>User ID:</b> <code>{user_info['id']}</code>

💡 <b>View your data:</b> <code>/data</code>
🔧 <b>Save more:</b> <code>/savedata</code>
            """
        else:
            return "❌ Failed to save data. Please try again."
    
    except Exception as e:
        return f"❌ Error saving data: {str(e)}"

def handle_cleardata(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /cleardata command - Clear user data"""
    
    user_id = user_info.get('id')
    
    # Clear all user data from Supabase
    success = bot.delete_user_data(user_id)
    
    if success:
        return """
🗑️ <b>Data Cleared Successfully!</b>

✅ All your saved data has been removed from the database.

💡 <b>What's cleared:</b>
• User preferences
• Session data
• Custom saved variables

🔧 <b>Start fresh:</b>
Use <code>/start</code> to begin again
Or <code>/savedata</code> to save new data
        """
    else:
        return """
❌ <b>Failed to Clear Data</b>

🚨 There was an error clearing your data.

💡 <b>Possible solutions:</b>
• Try again in a moment
• Contact admin if problem persists
• Your data might already be cleared
        """
