from app import Bot, User

def handle(user_info, chat_id, message_text):
    """Handle /notes command - notes management help"""
    
    return """
📝 <b>Notes Management System</b>

💾 <b>Save Note:</b>
<b>/save title | content</b>
• Saves a new note with title and content

📂 <b>Show Notes:</b>  
<b>/show</b>
• Shows all your notes
<b>/show 2</b>
• Shows page 2 of your notes

👀 <b>View Note:</b>
<b>/view note_id</b>
• View specific note details

🗑️ <b>Delete Note:</b>
<b>/delete note_id</b>  
• Permanently delete a note

💡 <b>Examples:</b>
• <b>/save Shopping | Milk, Eggs, Bread</b>
• <b>/show</b>
• <b>/view abc123</b>
• <b>/delete abc123</b>

🔒 <b>Your notes are stored securely in Supabase database!</b>
"""