from datetime import datetime
from app import User

def handle(user_info, chat_id, message_text):
    """Handle /show command - show user notes"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get page number from command if provided
    page = 1
    if message_text.startswith('/show'):
        parts = message_text.split()
        if len(parts) > 1:
            try:
                page = int(parts[1])
            except:
                pass
    
    # Get notes from Supabase
    notes = User.get_notes(user_id, page=page, limit=5)
    
    if not notes:
        return """
📭 <b>No Notes Found</b>

You haven't saved any notes yet!

💾 <b>To save a note:</b>
<b>/save title | content</b>

💡 <b>Example:</b>
<b>/save My Ideas | This is my first note content</b>
"""
    
    # Format notes
    notes_text = ""
    for note in notes:
        time_str = datetime.fromisoformat(note['created_at']).strftime('%m/%d %H:%M')
        category = note.get('category', 'general')
        content_preview = note['content'][:100] + "..." if len(note['content']) > 100 else note['content']
        
        notes_text += f"""
📄 <b>{note['title']}</b> [{category}]
🆔 <b>{note['id']}</b> | ⏰ {time_str}
📝 {content_preview}
"""
    
    total_pages = "..."  # In real implementation, calculate total pages
    
    return f"""
📂 <b>Your Notes</b> (Page {page})

👤 <b>User:</b> {first_name}
📊 <b>Total Notes:</b> {len(notes)}

{notes_text}
🔍 <b>View Note:</b> <b>/view note_id</b>
🗑️ <b>Delete Note:</b> <b>/delete note_id</b>
📄 <b>Next Page:</b> <b>/show {page + 1}</b>
"""