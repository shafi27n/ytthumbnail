from flask import jsonify

def handle_menu(user_info, chat_id, message_text):
    """Handle /menu command with interactive buttons"""
    
    user_name = user_info.get('first_name', 'User')
    
    response_text = f"""
🎯 <b>মেইন মেনু</b>

✨ স্বাগতম <b>{user_name}</b>!

নিচের বাটনগুলো থেকে আপনার পছন্দের অপশন সিলেক্ট করুন:

• <b>সহায়তা</b> - সব কমান্ডের তথ্য
• <b>শুরু করুন</b> - বট ব্যবহার শুরু করুন  
• <b>ফর্ম জমা দিন</b> - নাম ও ছবি জমা দিন

👇 <b>বাটন প্রেস করে নির্বাচন করুন:</b>
    """
    
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '🆘 সহায়তা', 'callback_data': 'menu_help'},
                {'text': '🚀 শুরু করুন', 'callback_data': 'menu_start'}
            ],
            [
                {'text': '📋 ফর্ম জমা দিন', 'callback_data': 'menu_form'}
            ],
            [
                {'text': '🔄 রিফ্রেশ মেনু', 'callback_data': 'menu_refresh'}
            ]
        ]
    }
    
    return jsonify({
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': response_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })

def handle_all_callbacks(callback_data, user_info, chat_id, message_id):
    """Handle all menu callbacks"""
    
    if callback_data == 'menu_help':
        return show_help_menu(chat_id, message_id)
    
    elif callback_data == 'menu_start':
        return show_start_menu(chat_id, message_id, user_info)
    
    elif callback_data == 'menu_form':
        return show_form_menu(chat_id, message_id)
    
    elif callback_data == 'menu_refresh':
        return refresh_main_menu(chat_id, message_id, user_info)
    
    elif callback_data == 'start_form_from_menu':
        # Return a new message to start form (can't edit message for session start)
        from .form import handle_form
        return handle_form(user_info, chat_id, "")
    
    elif callback_data == 'back_to_main':
        return refresh_main_menu(chat_id, message_id, user_info)
    
    return None

def show_help_menu(chat_id, message_id):
    """Show help information"""
    
    help_text = """
🆘 <b>সহায়তা মেনু</b>

📚 <b>সকল কমান্ড:</b>

• <code>/start</code> - বট শুরু করুন
• <code>/menu</code> - মেইন মেনু দেখুন  
• <code>/form</code> - ফর্ম জমা দিন
• <code>/help</code> - সহায়তা দেখুন
• <code>/cancel</code> - বর্তমান কাজ বাতিল করুন

ℹ️ <b>কিভাবে ব্যবহার করবেন:</b>
১. <b>/form</b> দিয়ে ফর্ম শুরু করুন
২. আপনার নাম লিখুন
৩. ছবি আপলোড করুন
৪. ডাটা অটোমেটিক গ্রুপে শেয়ার হবে
    """
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '📋 ফর্ম শুরু করুন', 'callback_data': 'start_form_from_menu'}],
            [{'text': '↩️ মেনুতে ফিরুন', 'callback_data': 'back_to_main'}]
        ]
    }
    
    return jsonify({
        'method': 'editMessageText',
        'chat_id': chat_id,
        'message_id': message_id,
        'text': help_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })

def show_start_menu(chat_id, message_id, user_info):
    """Show start information"""
    
    user_name = user_info.get('first_name', 'User')
    
    start_text = f"""
🚀 <b>বট শুরু করা হয়েছে!</b>

🎉 স্বাগতম <b>{user_name}</b>! এই বটের মাধ্যমে আপনি:

• 📋 <b>ফর্ম জমা</b> দিতে পারবেন
• 🖼️ <b>ছবি আপলোড</b> করতে পারবেন  
• 👥 <b>গ্রুপে ডাটা</b> শেয়ার করতে পারবেন

📌 <b>দ্রুত শুরু করতে:</b>
নিচের <b>'ফর্ম শুরু করুন'</b> বাটন প্রেস করুন
    """
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '📋 ফর্ম শুরু করুন', 'callback_data': 'start_form_from_menu'}],
            [{'text': '🆘 সহায়তা', 'callback_data': 'menu_help'}],
            [{'text': '↩️ মেনুতে ফিরুন', 'callback_data': 'back_to_main'}]
        ]
    }
    
    return jsonify({
        'method': 'editMessageText',
        'chat_id': chat_id,
        'message_id': message_id,
        'text': start_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })

def show_form_menu(chat_id, message_id):
    """Show form information"""
    
    form_text = """
📋 <b>ফর্ম সিস্টেম</b>

এই ফর্মের মাধ্যমে আপনি:

1. 📛 <b>আপনার নাম</b> জমা দিতে পারবেন
2. 🖼️ <b>আপনার ছবি</b> আপলোড করতে পারবেন  
3. 👥 <b>ডাটা গ্রুপে</b> শেয়ার করতে পারবেন

🔄 <b>কাজের ধাপ:</b>
1. ফর্ম শুরু করুন
2. নাম লিখুন
3. ছবি আপলোড করুন
4. অটোমেটিক গ্রুপে শেয়ার হবে

✅ ফর্ম শুরু করতে নিচের বাটন প্রেস করুন:
    """
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '🚀 ফর্ম শুরু করুন', 'callback_data': 'start_form_from_menu'}],
            [{'text': '🆘 সহায়তা', 'callback_data': 'menu_help'}],
            [{'text': '↩️ মেনুতে ফিরুন', 'callback_data': 'back_to_main'}]
        ]
    }
    
    return jsonify({
        'method': 'editMessageText',
        'chat_id': chat_id,
        'message_id': message_id,
        'text': form_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })

def refresh_main_menu(chat_id, message_id, user_info):
    """Refresh the main menu"""
    
    user_name = user_info.get('first_name', 'User')
    
    menu_text = f"""
🎯 <b>মেইন মেনু</b>

✨ স্বাগতম <b>{user_name}</b>!

নিচের বাটনগুলো থেকে আপনার পছন্দের অপশন সিলেক্ট করুন:

• <b>সহায়তা</b> - সব কমান্ডের তথ্য
• <b>শুরু করুন</b> - বট ব্যবহার শুরু করুন  
• <b>ফর্ম জমা দিন</b> - নাম ও ছবি জমা দিন

👇 <b>বাটন প্রেস করে নির্বাচন করুন:</b>
    """
    
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '🆘 সহায়তা', 'callback_data': 'menu_help'},
                {'text': '🚀 শুরু করুন', 'callback_data': 'menu_start'}
            ],
            [
                {'text': '📋 ফর্ম জমা দিন', 'callback_data': 'menu_form'}
            ],
            [
                {'text': '🔄 রিফ্রেশ মেনু', 'callback_data': 'menu_refresh'}
            ]
        ]
    }
    
    return jsonify({
        'method': 'editMessageText',
        'chat_id': chat_id,
        'message_id': message_id,
        'text': menu_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })
