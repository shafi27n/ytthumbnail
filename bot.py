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

def send_telegram_message(chat_id, text, parse_mode='Markdown'):
    """
    Telegram-এ মেসেজ সেন্ড করার জন্য সহায়ক ফাংশন
    """
    return {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }

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

        # GET request হ্যান্ডেল
        if request.method == 'GET':
            return jsonify({
                'status': 'Bot is running',
                'token_received': True
            })

        # POST request হ্যান্ডেল
        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            logger.info(f"Update received: {update}")
            
            # মেসেজ ডেটা এক্সট্র্যাক্ট
            chat_id = None
            message_text = ''
            
            if 'message' in update and 'text' in update['message']:
                chat_id = update['message']['chat']['id']
                message_text = update['message']['text']
            else:
                return jsonify({'ok': True})

            if not chat_id:
                return jsonify({'error': 'Chat ID not found'}), 400

            # শুধুমাত্র /start কমান্ড হ্যান্ডেল
            if message_text.startswith('/start'):
                welcome_text = """
🤖 **স্বাগতম!**

আমার নাম ইন্টার‍্যাক্টিভ বট। আমি আপনার কিছু তথ্য নেব।

আপনার নাম কি?
                """
                
                # ইউজার স্টেট সেটআপ শুরু
                user_states[chat_id] = {'step': 'asking_name'}
                
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=welcome_text
                ))

            # ইউজার স্টেট অনুযায়ী প্রসেস
            user_state = user_states.get(chat_id, {})
            current_step = user_state.get('step', None)

            if current_step == 'asking_name':
                user_states[chat_id] = {
                    'step': 'asking_age',
                    'name': message_text
                }
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=f"ধন্যবাদ {message_text}! আপনার বয়স কি?"
                ))

            elif current_step == 'asking_age':
                user_states[chat_id] = {
                    'step': None,
                    'name': user_state.get('name', 'অজানা'),
                    'age': message_text
                }
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=f"""✅ **প্রোফাইল সম্পূর্ণ!**

**নাম:** {user_state.get('name', 'অজানা')}
**বয়স:** {message_text}

আপনার প্রোফাইল সংরক্ষণ করা হয়েছে!"""
                ))

            # অন্য সব মেসেজের জন্য
            else:
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text="বট শুরু করতে /start কমান্ড ব্যবহার করুন"
                ))

    except Exception as e:
        logger.error(f'Error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
