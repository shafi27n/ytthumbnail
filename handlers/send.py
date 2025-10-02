import asyncio
from app import telegram_manager

def handle(user_info, chat_id, message_text):
    """Handle /send command - send message via specific account"""
    
    if not message_text.startswith('/send '):
        return """
📤 <b>Send Message</b>

📝 <b>Usage:</b>
<b>/send phone_number | target | message</b>

💡 <b>Examples:</b>
• <code>/send 1234567890 | username | Hello!</code>
• <code>/send 1234567890 | +123456789 | Hi there!</code>
• <code>/send 1234567890 | channel_name | Message</code>

🎯 <b>Target can be:</b>
• Username (without @)
• Phone number
• Channel/Group username
"""
    
    # Parse command
    parts = message_text[6:].split('|', 2)  # Remove "/send "
    if len(parts) < 3:
        return "❌ <b>Invalid format!</b> Use: <code>/send phone | target | message</code>"
    
    phone_number = parts[0].strip()
    target = parts[1].strip()
    message = parts[2].strip()
    
    user_id = user_info.get('id')
    
    # Send message
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success, result = loop.run_until_complete(
        telegram_manager.send_message_via_account(user_id, phone_number, target, message)
    )
    loop.close()
    
    return result