from app import User

def handle(user_info, chat_id, message_text):
    """Handle /delete command - delete specific note"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract note ID from command
    if message_text.startswith('/delete'):
        parts = message_text.split()
        if len(parts) < 2:
            return """
🗑️ <b>Delete Note</b>

📝 <b>Usage:</b> 
<b>/delete note_id</b>

💡 <b>Example:</b>
<b>/delete abc123</b>

⚠️ <b>Warning:</b> This action cannot be undone!

🔍 <b>First get note IDs with:</b> <b>/show</b>
"""
        note_id = parts[1].strip()
    else:
        return "❌ <b>Invalid usage!</b> Use: <b>/delete note_id</b>"
    
    # Delete note from Supabase
    success = User.delete_note(note_id, user_id)
    
    if success:
        return f"""
✅ <b>Note Deleted Successfully!</b>

🆔 <b>Deleted Note ID:</b> <b>{note_id}</b>
👤 <b>User:</b> {first_name}

🗑️ <b>Note has been permanently deleted.</b>

🔍 <b>View remaining notes:</b> <b>/show</b>
"""
    else:
        return f"""
❌ <b>Failed to delete note!</b>

🆔 <b>Note ID:</b> <b>{note_id}</b>

Possible reasons:
• Note doesn't exist
• Note doesn't belong to you
• Database error

🔍 <b>Check your notes:</b> <b>/show</b>
"""