from app import telegram_manager, run_async

def handle(user_info, chat_id, message_text):
    """Handle /send command - send message via specific account"""
    
    if not message_text.startswith('/send '):
        return """
📤 <b>Send Message</b>

📝 <b>Usage:</b>
<code>/send phone_number | target | message</code>

💡 <b>Examples:</b>
• <code>/send 1234567890 | username | Hello!</code>
• <code>/send 1234567890 | +123456789 | Hi there!</code>
• <code>/send 1234567890 | channel_name | Message</code>

🎯 <b>Target can be:</b>
• Username (without @)
• Phone number
• Channel/Group username

📋 <b>First get phone numbers from:</b> <code>/accounts</code>
"""
    
    # Parse command
    parts = message_text[6:].split('|', 2)  # Remove "/send "
    if len(parts) < 3:
        return "❌ <b>Invalid format!</b> Use: <code>/send phone | target | message</code>"
    
    phone_number = parts[0].strip()
    target = parts[1].strip()
    message = parts[2].strip()
    
    if not phone_number or not target or not message:
        return "❌ <b>Missing parameters!</b> Use: <code>/send phone | target | message</code>"
    
    user_id = user_info.get('id')
    
    # Send message using run_async helper
    success, result = run_async(
        telegram_manager.send_message_via_account(user_id, phone_number, target, message)
    )
    
    return result