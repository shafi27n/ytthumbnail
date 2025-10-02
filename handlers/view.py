from datetime import datetime
from app import User

def handle(user_info, chat_id, message_text):
    """Handle /view command - view specific note"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Extract note ID from command
    if message_text.startswith('/view'):
        parts = message_text.split()
        if len(parts) < 2:
            return """
👀 <b>View Note</b>

📝 <b>Usage:</b> 
<b>/view note_id</b>

💡 <b>Example:</b>
<b>/view abc123</b>

🔍 <b>First get note IDs with:</b> <b>/show</b>
"""
        note_id = parts[1].strip()
    else:
        return "❌ <b>Invalid usage!</b> Use: <b>/view note_id</b>"
    
    # Get note from Supabase
    note = User.get_note(note_id)
    
    if not note:
        return f"❌ <b>Note not found!</b> No note with ID: <b>{note_id}</b>"
    
    if note['user_id'] != user_id:
        return "❌ <b>Access denied!</b> This note doesn't belong to you."
    
    created_time = datetime.fromisoformat(note['created_at']).strftime('%Y-%m-%d %H:%M:%S')
    updated_time = datetime.fromisoformat(note['updated_at']).strftime('%Y-%m-%d %H:%M:%S') if note.get('updated_at') else created_time
    
    return f"""
📄 <b>Note Details</b>

🆔 <b>Note ID:</b> <b>{note['id']}</b>
📖 <b>Title:</b> {note['title']}
🏷️ <b>Category:</b> {note.get('category', 'general')}
📅 <b>Created:</b> {created_time}
🔄 <b>Updated:</b> {updated_time}

📝 <b>Content:</b>
{note['content']}

👤 <b>User:</b> {first_name}
🗑️ <b>Delete:</b> <b>/delete {note['id']}</b>
"""