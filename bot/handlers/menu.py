def handle_utils(user_info, chat_id, message_text):
    """Handle /utils command"""
    
    utils_text = f"""
🔧 <b>Utilities Menu</b>

👋 Hello <b>{user_info.get('first_name', 'User')}</b>!

🛠️ <b>Available Utilities:</b>
• Time display
• System status
• User information

🚀 <b>Multi-Command File:</b>
This file handles both <code>/utils</code> and <code>/tools</code> commands!

💡 <b>Try other commands:</b>
<code>/help</code> - Full command list
<code>/status</code> - System information
    """
    
    return utils_text

def handle_tools(user_info, chat_id, message_text):
    """Handle /tools command"""
    
    tools_text = f"""
🛠️ <b>Tools Menu</b>

🔨 <b>Available Tools:</b>
• Information display
• System monitoring

👤 <b>User Info:</b>
• User ID: <code>{user_info.get('id')}</code>
• Name: <b>{user_info.get('first_name', 'User')}</b>

💡 <b>This is part of multi-command file!</b>
    """
    
    return tools_text
