from bot.main import Bot

def handle_echo(user_info, chat_id, message_text):
    """Handle /echo command"""
    
    # Extract the text after /echo command
    echo_text = message_text[6:].strip() if len(message_text) > 6 else ""
    
    if not echo_text:
        return "📝 <b>Usage:</b> <code>/echo your message here</code>"
    
    # Save echo count
    from bot.main import User
    user_id = user_info.get('id')
    User.save_data(user_id, "echo_count", str(int(User.get_data(user_id, "echo_count") or 0) + 1))
    
    return f"""
🔊 <b>Echo Response:</b>

📝 <b>Your Message:</b>
<code>{echo_text}</code>

📊 <b>Stats:</b>
• Total Echos: {User.get_data(user_id, "echo_count") or 1}
• User: {user_info.get('first_name')}
"""