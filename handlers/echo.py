def handle_echo(user_info, chat_id, message_text):
    """Handle /echo command"""
    
    # Extract the text after /echo command
    echo_text = message_text[6:].strip() if len(message_text) > 6 else ""
    
    if not echo_text:
        return "📝 <b>Usage:</b> <code>/echo your message here</code>"
    
    return f"""
🔊 <b>Echo Response:</b>

📝 <b>Your Message:</b>
<code>{echo_text}</code>

📊 <b>User:</b> {user_info.get('first_name')}
✅ <b>Echo system working!</b>
"""