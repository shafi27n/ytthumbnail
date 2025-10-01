import requests
from bot.main import Bot, User, send_telegram_message, create_keyboard, create_inline_keyboard

def handle_advanced(user_info, chat_id, message_text):
    """Advanced command demonstrating all features"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Example of saving data
    bot_save_result = Bot.save_data("last_advanced_used", user_id)
    user_save_result = User.save_data(user_id, "advanced_usage_count", 
                                     str(int(User.get_data(user_id, "advanced_usage_count") or 0) + 1))
    
    # Create different types of keyboards
    reply_keyboard = create_keyboard([
        ["📊 Get Stats", "🛠️ Settings"],
        ["📝 Input Text", "❌ Cancel"]
    ])
    
    inline_keyboard = create_inline_keyboard([
        [{"text": "✅ Approve", "callback_data": "approve_123"}],
        [{"text": "❌ Deny", "callback_data": "deny_123"}, 
         {"text": "ℹ️ Info", "callback_data": "info_123"}],
        [{"text": "🌐 Website", "url": "https://example.com"}]
    ])
    
    response_text = f"""
🚀 <b>Advanced Command Demo</b>

👋 <b>Welcome {first_name}!</b>

📊 <b>System Status:</b>
• User ID: <code>{user_id}</code>
• Chat ID: <code>{chat_id}</code>
• Advanced Usage: <code>{User.get_data(user_id, 'advanced_usage_count') or 0}</code>

🔧 <b>Available Actions:</b>
1. <b>Run Command:</b> <code>Bot.runCommand()</code>
2. <b>Wait for Input:</b> <code>Bot.handleNextCommand()</code>
3. <b>Save Data:</b> Bot & User level
4. <b>Send Messages:</b> Text, Media, Files
5. <b>Keyboards:</b> Reply & Inline buttons
6. <b>HTTP Requests:</b> GET, POST, etc.

💾 <b>Data Save Results:</b>
• {bot_save_result}
• {user_save_result}

🎯 <b>Try these features:</b>
• Click buttons below
• Send <code>/advanced input</code> for input demo
• Send <code>/advanced http</code> for HTTP demo
"""

    # Return message with inline keyboard
    message_data = send_telegram_message(chat_id, response_text, parse_mode='HTML')
    message_data['reply_markup'] = inline_keyboard
    return message_data

def handle_adv(user_info, chat_id, message_text):
    """Alias for advanced command"""
    return handle_advanced(user_info, chat_id, message_text)