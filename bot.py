from flask import Flask, request, jsonify
import os
import logging

# লগিং কনফিগারেশন
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ইউজার স্টেট স্টোর করার জন্য ডিকশনারি
user_states = {}

def send_telegram_message(chat_id, text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=None):
    """
    Telegram-এ মেসেজ সেন্ড করার জন্য সহায়ক ফাংশন
    """
    return {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
        'reply_markup': reply_markup
    }

def get_main_menu():
    """
    মেইন মেনু বাটন তৈরি
    """
    return {
        'inline_keyboard': [
            [
                {'text': 'ℹ️ আমার সম্পর্কে', 'callback_data': 'about'},
                {'text': '📊 সার্ভিসেস', 'callback_data': 'services'}
            ],
            [
                {'text': '👤 প্রোফাইল', 'callback_data': 'profile'},
                {'text': '🛠️ সেটিংস', 'callback_data': 'settings'}
            ],
            [
                {'text': '📞 যোগাযোগ', 'callback_data': 'contact'}
            ]
        ]
    }

def get_services_menu():
    """
    সার্ভিসেস মেনু বাটন তৈরি
    """
    return {
        'inline_keyboard': [
            [
                {'text': '📝 নোট', 'callback_data': 'notes'},
                {'text': '🔄 কনভার্টার', 'callback_data': 'converter'}
            ],
            [
                {'text': '📊 ক্যালকুলেটর', 'callback_data': 'calculator'},
                {'text': '🎯 গেমস', 'callback_data': 'games'}
            ],
            [
                {'text': '🔙 মেনুতে ফিরে যান', 'callback_data': 'main_menu'}
            ]
        ]
    }

def answer_callback_query(callback_query_id, text, show_alert=False):
    """
    ক্যালব্যাক কুয়েরি উত্তর দেওয়ার জন্য সহায়ক ফাংশন
    """
    return {
        'method': 'answerCallbackQuery',
        'callback_query_id': callback_query_id,
        'text': text,
        'show_alert': show_alert
    }

def edit_message_reply_markup(chat_id, message_id, reply_markup):
    """
    মেসেজের রিপ্লাই মার্কআপ এডিট করার জন্য
    """
    return {
        'method': 'editMessageReplyMarkup',
        'chat_id': chat_id,
        'message_id': message_id,
        'reply_markup': reply_markup
    }

def edit_message_text(chat_id, message_id, text, parse_mode='Markdown', reply_markup=None):
    """
    মেসেজ টেক্সট এডিট করার জন্য
    """
    response = {
        'method': 'editMessageText',
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': parse_mode
    }
    if reply_markup:
        response['reply_markup'] = reply_markup
    return response

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    try:
        # URL থেকে টোকেন নেওয়া
        token = request.args.get('token')
        
        if not token:
            return jsonify({
                'error': 'Token required',
                'solution': 'Add ?token=YOUR_BOT_TOKEN to URL'
            }), 400

        # GET request হ্যান্ডেল - শুধু টোকেন ভ্যালিডেশন
        if request.method == 'GET':
            return jsonify({
                'status': 'Interactive Bot is running',
                'token_received': True,
                'message': 'Interactive Question-Answer Bot is ready!'
            })

        # POST request হ্যান্ডেল - টেলিগ্রাম আপডেট
        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            logger.info(f"Update received: {update}")
            
            # ক্যালব্যাক কুয়েরি হ্যান্ডেল
            if 'callback_query' in update:
                callback_data = update['callback_query']
                chat_id = callback_data['message']['chat']['id']
                message_id = callback_data['message']['message_id']
                callback_query_id = callback_data['id']
                data = callback_data['data']
                
                responses = []
                
                if data == 'main_menu':
                    # মেইন মেনু দেখাও
                    responses.append(
                        edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text="🏠 **মেইন মেনু**\n\nনিচের অপশন থেকে আপনার পছন্দের মেনু সিলেক্ট করুন:",
                            reply_markup=get_main_menu()
                        )
                    )
                    responses.append(answer_callback_query(callback_query_id, "মেইন মেনু"))
                
                elif data == 'about':
                    responses.append(
                        edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text="""ℹ️ **আমার সম্পর্কে**

🤖 **ইন্টার‍্যাক্টিভ বট**
এটি একটি ইন্টেলিজেন্ট ইন্টার‍্যাক্টিভ বট যা আপনার প্রশ্নের উত্তর দিতে পারে এবং বিভিন্ন সার্ভিস প্রদান করে।

🌟 **ফিচারস:**
• প্রশ্ন-উত্তর সিস্টেম
• বিভিন্ন ইউটিলিটি টুলস
• ইউজার-ফ্রেন্ডলি ইন্টারফেস
• রিয়েল-টাইম কমিউনিকেশন

💡 **ব্যবহার:** সরাসরি প্রশ্ন করুন অথবা মেনু থেকে সার্ভিস সিলেক্ট করুন।""",
                            reply_markup=get_main_menu()
                        )
                    )
                    responses.append(answer_callback_query(callback_query_id, "আমার সম্পর্কে তথ্য"))
                
                elif data == 'services':
                    responses.append(
                        edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text="""📊 **সার্ভিসেস মেনু**

নিচের সার্ভিসগুলো থেকে আপনার পছন্দেরটি সিলেক্ট করুন:

• 📝 **নোট** - নোট সংরক্ষণ ও ব্যবস্থাপনা
• 🔄 **কনভার্টার** - বিভিন্ন ইউনিট কনভার্সন
• 📊 **ক্যালকুলেটর** - গাণিতিক ক্যালকুলেশন
• 🎯 **গেমস** - মজাদার গেমস

সার্ভিস সিলেক্ট করতে নিচের বাটন ব্যবহার করুন:""",
                            reply_markup=get_services_menu()
                        )
                    )
                    responses.append(answer_callback_query(callback_query_id, "সার্ভিসেস মেনু"))
                
                elif data == 'profile':
                    # ইউজার প্রোফাইল দেখাও
                    user_state = user_states.get(chat_id, {})
                    name = user_state.get('name', 'অজানা')
                    age = user_state.get('age', 'অজানা')
                    
                    responses.append(
                        edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=f"""👤 **আপনার প্রোফাইল**

📛 **নাম:** {name}
🎂 **বয়স:** {age}
🆔 **ইউজার আইডি:** `{chat_id}`
📅 **রেজিস্ট্রেশন:** {'সম্পন্ন' if user_state else 'অসম্পূর্ণ'}

💡 **প্রোফাইল আপডেট করতে** `/profile` কমান্ড ব্যবহার করুন।""",
                            reply_markup=get_main_menu()
                        )
                    )
                    responses.append(answer_callback_query(callback_query_id, "প্রোফাইল তথ্য"))
                
                elif data == 'settings':
                    responses.append(
                        edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text="""🛠️ **সেটিংস**

⚙️ **সেটিংস অপশন:**
• 🔔 নোটিফিকেশন সেটিংস
• 🌐 ভাষা সেটিংস
• 🔒 প্রাইভেসি সেটিংস
• 📱 থিম সেটিংস

🔧 **সেটিংস কনফিগার করতে** সরাসরি মেসেজের মাধ্যমে আমাকে জানান।""",
                            reply_markup=get_main_menu()
                        )
                    )
                    responses.append(answer_callback_query(callback_query_id, "সেটিংস মেনু"))
                
                elif data == 'contact':
                    responses.append(
                        edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text="""📞 **যোগাযোগ**

📧 **ইমেইল:** example@email.com
🌐 **ওয়েবসাইট:** www.example.com
📱 **ফোন:** +8801XXXXXXXXX

💬 **সাপোর্ট:** সরাসরি মেসেজের মাধ্যমে যোগাযোগ করুন।

📍 **ঠিকানা:** 
আপনার প্রতিষ্ঠানের ঠিকানা
ঢাকা, বাংলাদেশ""",
                            reply_markup=get_main_menu()
                        )
                    )
                    responses.append(answer_callback_query(callback_query_id, "যোগাযোগ তথ্য"))
                
                elif data in ['notes', 'converter', 'calculator', 'games']:
                    service_names = {
                        'notes': '📝 নোট ম্যানেজার',
                        'converter': '🔄 ইউনিট কনভার্টার',
                        'calculator': '📊 ক্যালকুলেটর',
                        'games': '🎯 গেমস'
                    }
                    
                    service_name = service_names.get(data, data)
                    responses.append(
                        edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=f"🔄 **{service_name}**\n\nএই সার্ভিসটি খুব শীঘ্রই আসছে! 🚀\n\nবর্তমানে ডেভেলপমেন্ট চলছে। আপাতত মেইন মেনু থেকে অন্য সার্ভিস ব্যবহার করুন।",
                            reply_markup=get_services_menu()
                        )
                    )
                    responses.append(answer_callback_query(callback_query_id, f"{service_name} সার্ভিস"))
                
                # একাধিক রেসপন্স থাকলে array রিটার্ন দাও, নাহলে single object
                if len(responses) > 1:
                    return jsonify(responses)
                else:
                    return jsonify(responses[0])
            
            # মেসেজ ডেটা এক্সট্র্যাক্ট
            chat_id = None
            message_text = ''
            
            if 'message' in update and 'text' in update['message']:
                chat_id = update['message']['chat']['id']
                message_text = update['message']['text']
            elif 'channel_post' in update and 'text' in update['channel_post']:
                chat_id = update['channel_post']['chat']['id']
                message_text = update['channel_post']['text']
            else:
                return jsonify({'ok': True})  # Ignore non-text messages

            if not chat_id:
                return jsonify({'error': 'Chat ID not found'}), 400

            # ইউজার স্টেট চেক
            user_state = user_states.get(chat_id, {})
            current_step = user_state.get('step', None)

            # /start কমান্ড হ্যান্ডেল
            if message_text.startswith('/start'):
                welcome_text = """
🤖 **স্বাগতম ইন্টার‍্যাক্টিভ বট এ!** 🤖

আমি একটি ইন্টেলিজেন্ট বট যে আপনার প্রশ্নের উত্তর দিতে এবং বিভিন্ন সার্ভিস প্রদান করতে পারি।

🎯 **আমা�� যা করতে পারি:**
• আপনার প্রশ্নের উত্তর দিতে
• বিভিন্ন ইউটিলিটি সার্ভিস প্রদান করতে
• আপনার তথ্য সংরক্ষণ করতে
• ইন্টার‍্যাক্টিভ কমিউনিকেশন করতে

📋 **ব্যবহার বিধি:**
1. সরাসরি প্রশ্ন করুন
2. মেনু থেকে সার্ভিস সিলেক্ট করুন  
3. ধাপে ধাপে নির্দেশনা অনুসরণ করুন

👇 **শুরু করতে নিচের মেনু ব্যবহার করুন:**
                """
                
                # ইউজার স্টেট রিসেট
                user_states[chat_id] = {'step': None}
                
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=welcome_text,
                    reply_markup=get_main_menu()
                ))

            # /help কমান্ড হ্যান্ডেল
            elif message_text.startswith('/help'):
                help_text = """
🆘 **সাহায্য:** 🆘

📖 **কমান্ড লিস্ট:**
• `/start` - বট শুরু করুন
• `/help` - সাহায্য দেখুন  
• `/profile` - প্রোফাইল সেটআপ
• `/menu` - মেইন মেনু দেখুন

💡 **কিভাবে ব্যবহার করবেন:**
1. সরাসরি যেকোনো প্রশ্ন করুন
2. মেনু থেকে সার্ভিস সিলেক্ট করুন
3. বটের প্রশ্নের উত্তর দিন ধাপে ধাপে

🎯 **উদাহরণ:**
• "আপনার নাম কি?"
• "আজকের তারিখ কি?"
• "ক্যালকুলেটর ব্যবহার করতে চাই"

🛠️ **সাপোর্ট:** সমস্যা হলে /start কমান্ড দিয়ে আবার শুরু করুন।
                """
                
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=help_text,
                    reply_markup=get_main_menu()
                ))

            # /profile কমান্ড হ্যান্ডেল
            elif message_text.startswith('/profile'):
                user_states[chat_id] = {'step': 'asking_name'}
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text="👤 **প্রোফাইল সেটআপ**\n\nআপনার নাম কি? 📛\n\n(প্রতিটি ধাপে শুধু উত্তরটি লিখুন)"
                ))

            # /menu কমান্ড হ্যান্ডেল
            elif message_text.startswith('/menu'):
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text="🏠 **মেইন মেনু**\n\nনিচের অপশন থেকে আপনার পছন্দের মেনু সিলেক্ট করুন:",
                    reply_markup=get_main_menu()
                ))

            # ইউজার স্টেট অনুযায়ী প্রসেস
            elif current_step == 'asking_name':
                user_states[chat_id] = {
                    'step': 'asking_age',
                    'name': message_text
                }
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=f"ধন্যবাদ {message_text}! 🎉\n\nএখন আপনার বয়স কি? 🎂"
                ))

            elif current_step == 'asking_age':
                user_states[chat_id] = {
                    'step': None,
                    'name': user_state.get('name', 'অজানা'),
                    'age': message_text
                }
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=f"""✅ **প্রোফাইল সম্পূর্ণ!** ✅

👤 **প্রোফাইল তথ্য:**
📛 **নাম:** {user_state.get('name', 'অজানা')}
🎂 **বয়স:** {message_text}

আপনার প্রোফাইল সফলভাবে সংরক্ষণ করা হয়েছে! 🎉
প্রোফাইল দেখতে মেনু থেকে '👤 প্রোফাইল' সিলেক্ট করুন।""",
                    reply_markup=get_main_menu()
                ))

            # সাধারণ প্রশ্নের উত্তর
            else:
                # সাধারণ প্রশ্নের উত্তর দেওয়া
                responses = []
                
                # কিছু কমন প্রশ্নের উত্তর
                question = message_text.lower()
                
                if any(word in question for word in ['নাম', 'name', 'কে']):
                    responses.append(send_telegram_message(
                        chat_id=chat_id,
                        text="🤖 **আমার নাম ইন্টার‍্যাক্টিভ বট!**\n\nআমি আপনার ব্যক্তিগত সহায়ক বট। আপনি কীভাবে সাহায্য চান?",
                        reply_markup=get_main_menu()
                    ))
                
                elif any(word in question for word in ['হেলো', 'hello', 'হাই', 'hi']):
                    responses.append(send_telegram_message(
                        chat_id=chat_id,
                        text="👋 **হ্যালো!**\n\nআমাকে জিজ্ঞাসা করুন, আমি কীভাবে আপনাকে সাহায্য করতে পারি? 😊",
                        reply_markup=get_main_menu()
                    ))
                
                elif any(word in question for word in ['ধন্যবাদ', 'thank', 'thanks']):
                    responses.append(send_telegram_message(
                        chat_id=chat_id,
                        text="😊 **আপনাকেও ধন্যবাদ!**\n\nআর কোনো সাহায্যের প্রয়োজন হলে জানাবেন।",
                        reply_markup=get_main_menu()
                    ))
                
                elif any(word in question for word in ['সময়', 'time', 'তারিখ', 'date']):
                    from datetime import datetime
                    now = datetime.now()
                    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    responses.append(send_telegram_message(
                        chat_id=chat_id,
                        text=f"🕒 **বর্তমান সময় ও তারিখ:**\n\n`{current_time}`\n\nবাংলাদেশ সময় অনুযায়ী",
                        reply_markup=get_main_menu()
                    ))
                
                else:
                    # ডিফল্ট রেসপন্স
                    responses.append(send_telegram_message(
                        chat_id=chat_id,
                        text=f"""❓ **আপনার প্রশ্ন:** "{message_text}"

আমি এই প্রশ্নের সরাসরি উত্তর দিতে পারছি না। তবে আপনি যা করতে পারেন:

1. 🏠 **মেনু থেকে সার্ভিস সিলেক্ট করুন**
2. 📋 **স্পেসিফিক প্রশ্ন করুন**
3. 🛠️ **সাহায্যের জন্য** `/help` কমান্ড ব্যবহার করুন

অথবা সরাসরি আমাকে বলুন আপনি কী করতে চান? 😊""",
                        reply_markup=get_main_menu()
                    ))
                
                return jsonify(responses[0])

    except Exception as e:
        logger.error(f'Global error: {e}')
        return jsonify({
            'error': 'Processing failed',
            'details': str(e)
        }), 500

# অন্য কোন এন্ডপয়েন্টে রিকোয়েস্ট আসলে শুধু token চেক করবে
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    if request.method == 'GET':
        return jsonify({
            'status': 'Interactive Bot is running',
            'token_received': True,
            'endpoint': path
        })
    
    # POST request এর জন্য মূল লজিকে redirect
    return handle_request()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
