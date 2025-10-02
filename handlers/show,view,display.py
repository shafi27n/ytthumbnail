from datetime import datetime

def show_data_function(user_info, chat_id, message_text):
    """Handle /show, /display, /view commands - SAME FILE"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    command_used = message_text.split()[0] if message_text else "/show"
    
    response_text = f"""
📂 <b>Data Display System</b>

🔧 <b>Command Details:</b>
• File: show,display,view.py
• Function: show_data_function()
• Command Used: <code>{command_used}</code>

👤 <b>User Info:</b>
• Name: {first_name}
• ID: <code>{user_id}</code>
• Time: {datetime.now().strftime('%H:%M:%S')}

📊 <b>Your Saved Data:</b>
• Item 1: Sample data 1
• Item 2: Sample data 2
• Item 3: Sample data 3

🎯 <b>Equivalent Commands:</b>
• <code>/show</code> - Display data
• <code>/display</code> - Display data
• <code>/view</code> - Display data

💡 <b>System Working:</b>
✅ Multiple commands, single file
✅ Same function handles all commands
✅ File: show,display,view.py

🚀 <b>All display commands work identically!</b>
"""
    
    return response_text