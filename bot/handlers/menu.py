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
                {'text': '🔄 রিফ্রেশ মেনু', 'callback_data': 'menu_refresh'},
                {'text': '❓ সাহায্য', 'callback_data': 'menu_help'}
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

def handle_callback(callback_data, user_info, chat_id, message_id):
    """Handle menu button callbacks"""
    
    if callback_data == 'menu_help':
        return edit_menu_with_command(chat_id, message_id, "help")
    
    elif callback_data == 'menu_start':
        return edit_menu_with_command(chat_id, message_id, "start")
    
    elif callback_data == 'menu_form':
        return edit_menu_with_command(chat_id, message_id, "form")
    
    elif callback_data == 'menu_refresh':
        return refresh_menu(chat_id, message_id, user_info)
    
    return None

def edit_menu_with_command(chat_id, message_id, command_name):
    """Edit menu and show command execution message"""
    
    command_messages = {
        'help': {
            'text': """
🆘 <b>সহায়তা মেনু</b>

📚 <b>সকল কমান্ড:</b>

• <code>/start</code> - বট শুরু করুন
• <code>/menu</code> - মেইন মেনু দেখুন  
• <code>/form</code> - ফর্ম জমা দিন
• <code>/help</code> - সহায়তা দেখুন
• <code>/cancel</code> - বর্তমান কাজ বাতিল করুন

ℹ️ <b>মেনুতে ফিরতে:</b> /menu
            """,
            'buttons': [
                [{'text': '↩️ মেনুতে ফিরুন', 'callback_data': 'menu_refresh'}]
            ]
        },
        'start': {
            'text': f"""
🚀 <b>বট শুরু করা হয়েছে!</b>

🎉 স্বাগতম! এই বটের মাধ্যমে আপনি:

• 📋 ফর্ম জমা দিতে পারবেন
• 🖼️ ছবি আপলোড করতে পারবেন
• 👥 গ্রুপে ডাটা শেয়ার করতে পারবেন

📌 <b>মেনু থেকে অপশন সিলেক্ট করুন:</b>
            """,
            'buttons': [
                [{'text': '📋 ফর্ম জমা দিন', 'callback_data': 'menu_form'}],
                [{'text': '↩️ মেনুতে ফিরুন', 'callback_data': 'menu_refresh'}]
            ]
        },
        'form': {
            'text': """
📋 <b>ফর্ম সিস্টেম</b>

এই ফর্মের মাধ্যমে আপনি:

1. আপনার নাম জমা দিতে পারবেন
2. আপনার ছবি আপলোড করতে পারবেন  
3. ডাটা গ্রুপে শেয়ার করতে পারবেন

✅ ফর্ম শুরু করতে নিচের বাটন প্রেস করুন:
            """,
            'buttons': [
                [{'text': '📝 ফর্ম শুরু করুন', 'callback_data': 'start_form'}],
                [{'text': '↩️ মেনুতে ফিরুন', 'callback_data': 'menu_refresh'}]
            ]
        }
    }
    
    if command_name in command_messages:
        message_data = command_messages[command_name]
        
        keyboard = {
            'inline_keyboard': message_data['buttons']
        }
        
        return jsonify({
            'method': 'editMessageText',
            'chat_id': chat_id,
            'message_id': message_id,
            'text': message_data['text'],
            'parse_mode': 'HTML',
            'reply_markup': keyboard
        })

def refresh_menu(chat_id, message_id, user_info):
    """Refresh the main menu"""
    
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
                {'text': '🔄 রিফ্রেশ মেনু', 'callback_data': 'menu_refresh'},
                {'text': '❓ সাহায্য', 'callback_data': 'menu_help'}
            ]
        ]
    }
    
    return jsonify({
        'method': 'editMessageText',
        'chat_id': chat_id,
        'message_id': message_id,
        'text': response_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    })

# Special handler for starting form from menu
def handle_start_form_callback(callback_data, user_info, chat_id, message_id):
    """Handle direct form start from menu"""
    
    if callback_data == 'start_form':
        # Send a new message to start the form (can't edit to start session properly)
        from .form import handle_form
        return handle_form(user_info, chat_id, "")
    
    return None

# Handle combined callbacks
def handle_all_callbacks(callback_data, user_info, chat_id, message_id):
    """Handle all callback types"""
    
    # First try menu callbacks
    result = handle_callback(callback_data, user_info, chat_id, message_id)
    if result:
        return result
    
    # Then try form start callback
    result = handle_start_form_callback(callback_data, user_info, chat_id, message_id)
    if result:
        return result
    
    return None
