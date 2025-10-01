from flask import jsonify

def handle_start(user_info, chat_id, message_text):
    """Handle /start command"""
    
    user_name = user_info.get('first_name', 'User')
    user_id = user_info.get('id')
    
    welcome_text = f"""
🎉 <b>স্বাগতম {user_name}!</b>

🤖 <b>আমার সম্পর্কে:</b>
আমি একটি স্মার্ট টেলিগ্রাম বট যার মাধ্যমে আপনি:

• 📋 <b>ফর্ম জমা</b> দিতে পারবেন
• 🖼️ <b>ছবি আপলোড</b> করতে পারবেন  
• 👥 <b>গ্রুপে ডাটা</b> শেয়ার করতে পারবেন
• 📰 <b>সর্বশেষ খবর</b> দেখতে পারবেন
• 🎯 <b>ইন্টারেক্টিভ মেনু</b> ব্যবহার করতে পারবেন

👤 <b>আপনার তথ্য:</b>
• <b>নাম:</b> {user_name}
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>

👇 <b>মেনু থেকে শুরু করুন:</b>
    """
    
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '📱 মেইন মেনু', 'callback_data': 'menu_refresh'},
                {'text': '📋 ফর্ম জমা দিন', 'callback_data': 'start_form'}
            ],
            [
                {'text': '📰 সর্বশেষ খবর', 'callback_data': 'news_refresh'},
                {'text': '🆘 সহায়তা', 'callback_data': 'menu_help'}
            ]
        ]
    }
    
    return jsonify({
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': welcome_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })

def handle_all_callbacks(callback_data, user_info, chat_id, message_id):
    """Handle start-related callbacks"""
    
    if callback_data == 'start_quick':
        # Quick start from callback - edit current message
        user_name = user_info.get('first_name', 'User')
        
        welcome_text = f"""
🎉 <b>স্বাগতম {user_name}!</b>

🤖 বটটি ব্যবহার করতে নিচের অপশনগুলো ব্যবহার করুন:

• <b>মেনু</b> - সব অপশন একসাথে
• <b>ফর্ম</b> - ডাটা জমা দিন  
• <b>খবর</b> - সর্বশেষ আপডেট
• <b>সাহায্য</b> - গাইডলাইন

👇 <b>এখন কি করতে চান?</b>
        """
        
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': '📱 মেইন মেনু', 'callback_data': 'menu_refresh'},
                    {'text': '📋 ফর্ম জমা দিন', 'callback_data': 'start_form'}
                ],
                [
                    {'text': '📰 সর্বশেষ খবর', 'callback_data': 'news_refresh'},
                    {'text': '🆘 সহায়তা', 'callback_data': 'menu_help'}
                ]
            ]
        }
        
        return jsonify({
            'method': 'editMessageText',
            'chat_id': chat_id,
            'message_id': message_id,
            'text': welcome_text,
            'parse_mode': 'HTML',
            'reply_markup': keyboard
        })
    
    return None
