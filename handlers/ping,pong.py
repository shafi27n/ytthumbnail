from datetime import datetime

def ping_pong_test_function(user_info, chat_id, message_text):
    """Handle /ping, /pong, /test commands - SAME FILE"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    command_used = message_text.split()[0] if message_text else "/ping"
    
    response_text = f"""
🏓 <b>Ping-Pong-Test System</b>

🔧 <b>Command Details:</b>
• File: ping,pong,test.py
• Function: ping_pong_test_function()
• Command Used: <code>{command_used}</code>

👤 <b>User Info:</b>
• Name: {first_name}
• ID: <code>{user_id}</code>
• Time: {datetime.now().strftime('%H:%M:%S')}

🎯 <b>Multiple Commands Demo:</b>

Try these equivalent commands:
• <code>/ping</code> - This response
• <code>/pong</code> - Same response  
• <code>/test</code> - Same response

✅ <b>All commands execute the same function!</b>

💡 <b>System Proof:</b>
Same file handles: ping, pong, test
Different commands, identical output
"""

    return response_text