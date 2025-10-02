from datetime import datetime
from app import Bot, User

def handle(user_info, chat_id, message_text):
    """Handle /save command - save user notes"""
    
    user_id = user_info.get('id')
    username = user_info.get('username', '')
    first_name = user_info.get('first_name', 'User')
    
    # If no message text provided, wait for user input
    if not message_text or message_text == "/save":
        return Bot.handleNextCommand("save", user_info, chat_id)
    
    # Extract data after /save command (if provided directly)
    note_data = message_text[6:].strip() if message_text.startswith('/save') else message_text
    
    if not note_data:
        return """
💾 <b>Save Note</b>

📝 <b>Usage:</b> 
<b>/save title | content</b>

💡 <b>Examples:</b>
• <b>/save Shopping List | Milk, Eggs, Bread</b>
• <b>/save Important Ideas | My project ideas...</b>
• <b>/save Meeting Notes | Discussed new features</b>

🔧 <b>Format:</b> title | content
"""
    
    # Parse title and content
    if '|' in note_data:
        parts = note_data.split('|', 1)
        title = parts[0].strip()
        content = parts[1].strip()
    else:
        # If no | separator, use first line as title, rest as content
        lines = note_data.split('\n', 1)
        title = lines[0].strip()[:50]  # Limit title length
        content = lines[1].strip() if len(lines) > 1 else "No content provided"
    
    if not title:
        return "❌ <b>Title is required!</b> Please provide a title for your note."
    
    # Save note to Supabase
    result = User.save_note(user_id, username, title, content)
    
    if result:
        return f"""
✅ <b>Note Saved Successfully!</b>

📖 <b>Title:</b> {title}
📝 <b>Content:</b>
<b>{content}</b>

👤 <b>User:</b> {first_name}
🆔 <b>Note ID:</b> <b>{result.get('id', 'N/A')}</b>
📅 <b>Saved:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔍 <b>View notes:</b> <b>/show</b>
"""
    else:
        return "❌ <b>Failed to save note!</b> Please try again later."