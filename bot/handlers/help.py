from flask import jsonify

def handle_help(user_info, chat_id, message_text):
    """Handle /help command"""
    
    response_text = """
🆘 <b>বট সহায়তা</b>

📚 <b>সকল কমান্ড:</b>

• <code>/start</code> - বট শুরু করুন
• <code>/menu</code> - ইন্টারেক্টিভ মেনু দেখুন
• <code>/form</code> - নাম ও ছবি জমা দিন
• <code>/help</code> - এই মেসেজ দেখুন
• <code>/cancel</code> - বর্তমান কাজ বাতিল করুন

🛠️ <b>মেনু সিস্টেম:</b>
মেনু থেকে সবকিছু এক ক্লিকেই এক্সেস করুন!

👇 <b>মেনু খুলুন:</b>
    """
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '📱 মেইন মেনু', 'callback_data': 'menu_refresh'}]
        ]
    }
    
    return jsonify({
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': response_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })
