def handle(user_info, chat_id, message_text):
    """Handle /install command - setup system"""
    
    from app import setup_tables
    
    return """
🔧 <b>System Installation</b>

✅ <b>Database tables are automatically created on startup!</b>

📊 <b>Current Status:</b>
• Command system: ✅ Loaded
• Database setup: ✅ Automated
• Notes system: ✅ Ready

🚀 <b>You can now use:</b>
• <b>/save</b> - Save notes
• <b>/show</b> - View notes  
• <b>/view</b> - View specific note
• <b>/delete</b> - Delete notes

💡 <b>Get started with:</b>
<b>/save My Note | This is my first note</b>
"""