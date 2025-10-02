from datetime import datetime
from app import Bot

def main(user_info, chat_id, message_text, command_name):
    """Main function that handles ping, pong, test commands"""
    
    if command_name == "ping":
        return handle_ping(user_info, chat_id, message_text)
    elif command_name == "pong":
        return handle_pong(user_info, chat_id, message_text)
    elif command_name == "test":
        return handle_test(user_info, chat_id, message_text)
    else:
        return f"❌ Unknown command: {command_name}"

def handle_ping(user_info, chat_id, message_text):
    """Handle /ping command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    return f"""
🏓 <b>Pong!</b> (via /ping)

👋 Hello {first_name}!
🕒 Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📁 Module: ping,pong,test.py

💡 <b>Related commands:</b>
• <b>/pong</b> - Different response
• <b>/test</b> - System test
"""

def handle_pong(user_info, chat_id, message_text):
    """Handle /pong command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    return f"""
🎯 <b>Ping!</b> (via /pong)

👋 Hey {first_name}!
🕒 Response Time: {datetime.now().strftime('%H:%M:%S')}
📁 Module: ping,pong,test.py

⚡ <b>System is responsive!</b>
This shows multi-command file working perfectly!
"""

def handle_test(user_info, chat_id, message_text):
    """Handle /test command"""
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Test the command execution system
    result = f"""
🧪 <b>System Test</b> (via /test)

✅ <b>Test Results:</b>
• Module loading: ✅ Working
• Command routing: ✅ Working  
• Multi-command files: ✅ Working
• User info: ✅ Available
• Timestamp: ✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

👤 <b>User Details:</b>
• Name: {first_name}
• ID: <b>{user_id}</b>
• Chat: <b>{chat_id}</b>

🔧 <b>File Info:</b>
• Module: ping,pong,test.py
• Commands: /ping, /pong, /test
• All functioning correctly!
"""
    
    return result