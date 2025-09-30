from flask import jsonify

def handle_start(user_info, chat_id, message_text):
    """Handle /start command"""
    
    user_name = user_info.get('first_name', 'User')
    
    response_text = f"""
🎉 <b>স্বাগতম {user_name}!</b>

🤖 এই বটের মাধ্যমে আপনি সহজেই:
• 📋 ফর্ম জমা দিতে পারবেন
• 🖼️ ছবি আপলোড করতে পারবেন  
• 👥 গ্রুপে ডাটা শেয়ার করতে পারবেন

📱 <b>দ্রুত এক্সেসের জন্য:</b>
• <b>/menu</b> - ইন্টারেক্টিভ মেনু
• <b>/form</b> - ফর্ম জমা দিন
• <b>/help</b> - সহায়তা

👇 <b>মেনু দিয়ে শুরু করুন:</b>
    """
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '📱 মেনু খুলুন', 'callback_data': 'menu_refresh'}]
        ]
    }
    
    return jsonify({
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': response_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })
