import requests
import json
from flask import jsonify
from datetime import datetime
import os

# Global session storage
SESSIONS = {}

def handle_form(user_info, chat_id, message_text):
    """Handle /form command - collect user name and photo"""
    
    user_id = user_info.get('id')
    
    # Start form session
    SESSIONS[user_id] = {
        'waiting_for': 'form_name',
        'command': 'form',
        'data': {
            'step': 1,
            'user_info': user_info
        }
    }
    
    response_text = f"""
📋 <b>ফর্ম সিস্টেম</b>

✨ <b>স্বাগতম {user_info.get('first_name', 'User')}!</b>

আপনার তথ্য সংগ্রহ করা হবে ২টি ধাপে:

<b>ধাপ ১:</b> আপনার পুরো নাম লিখুন
<b>ধাপ ২:</b> আপনার ছবি আপলোড করুন

📝 <b>প্রথম ধাপ:</b> আপনার <b>পুরো নাম</b> টাইপ করে সেন্ড দিন:
    """
    
    return jsonify({
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': response_text,
        'parse_mode': 'HTML'
    })

def handle_text(message):
    """Handle text messages for form name input"""
    user_id = message.get('from', {}).get('id')
    
    if user_id in SESSIONS and SESSIONS[user_id]['waiting_for'] == 'form_name':
        user_input = message.get('text', '').strip()
        
        if not user_input:
            return jsonify({
                'method': 'sendMessage',
                'chat_id': message['chat']['id'],
                'text': "❌ <b>খালি নাম গ্রহণযোগ্য নয়!</b>\n\nআপনার সঠিক নাম লিখুন:",
                'parse_mode': 'HTML'
            })
        
        # Store name and move to photo step
        SESSIONS[user_id]['data']['name'] = user_input
        SESSIONS[user_id]['waiting_for'] = 'form_photo'
        SESSIONS[user_id]['data']['step'] = 2
        
        response_text = f"""
✅ <b>নাম সংরক্ষণ করা হয়েছে!</b>

👤 <b>নাম:</b> {user_input}

📸 <b>ধাপ ২:</b> এখন আপনার একটি <b>ছবি</b> আপলোড করুন।

<code>ছবি সিলেক্ট করে সেন্ড দিন...</code>
        """
        
        return jsonify({
            'method': 'sendMessage',
            'chat_id': message['chat']['id'],
            'text': response_text,
            'parse_mode': 'HTML'
        })
    
    return None

def handle_photo(message):
    """Handle photo upload for form"""
    user_id = message.get('from', {}).get('id')
    
    if user_id in SESSIONS and SESSIONS[user_id]['waiting_for'] == 'form_photo':
        try:
            # Get the largest available photo
            photos = message.get('photo', [])
            if not photos:
                return jsonify({
                    'method': 'sendMessage',
                    'chat_id': message['chat']['id'],
                    'text': "❌ <b>ছবি লোড করা যায়নি!</b>\n\nদয়া করে আবার ছবি সেন্ড করুন:",
                    'parse_mode': 'HTML'
                })
            
            # Get the best quality photo (last in array is largest)
            photo_info = photos[-1]
            file_id = photo_info.get('file_id')
            
            # Store photo file_id
            SESSIONS[user_id]['data']['photo_file_id'] = file_id
            
            # Process and send to group
            return process_form_completion(user_id, message['chat']['id'])
            
        except Exception as e:
            error_msg = f"❌ <b>ত্রুটি:</b> ছবি প্রসেস করতে সমস্যা হয়েছে\n\n<code>{str(e)}</code>"
            return jsonify({
                'method': 'sendMessage',
                'chat_id': message['chat']['id'],
                'text': error_msg,
                'parse_mode': 'HTML'
            })
    
    return None

def send_to_telegram_api(method, data):
    """Send actual request to Telegram API"""
    try:
        bot_token = os.environ.get('BOT_TOKEN')
        if not bot_token:
            print("❌ BOT_TOKEN not found in environment variables")
            return None
            
        url = f"https://api.telegram.org/bot{bot_token}/{method}"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram API request successful: {method}")
            return response.json()
        else:
            print(f"❌ Telegram API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error sending to Telegram API: {e}")
        return None

def process_form_completion(user_id, chat_id):
    """Process completed form and send to group"""
    try:
        user_data = SESSIONS[user_id]['data']
        name = user_data.get('name', 'N/A')
        photo_file_id = user_data.get('photo_file_id')
        user_info = user_data.get('user_info', {})
        
        # Group ID - আপনার আসল গ্রুপ ইউজারনেম বা ID দিয়ে পরিবর্তন করুন
        GROUP_ID = "@refffrrr"  # অথবা "-123456789" গ্রুপ ID
        
        # Prepare message for group
        group_message = f"""
📋 <b>নতুন ফর্ম সাবমিশন</b>

👤 <b>ব্যবহারকারী:</b> {user_info.get('first_name', 'N/A')}
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>নাম:</b> {name}
📅 <b>সময়:</b> {get_current_time()}

✅ ফর্ম সম্পূর্ণ হয়েছে!
        """
        
        # ACTUALLY SEND PHOTO TO GROUP
        group_data = {
            'chat_id': GROUP_ID,
            'photo': photo_file_id,
            'caption': group_message,
            'parse_mode': 'HTML'
        }
        
        # Send photo to group via Telegram API
        group_result = send_to_telegram_api('sendPhoto', group_data)
        
        if not group_result:
            # If group send fails, try sending as text message
            text_data = {
                'chat_id': GROUP_ID,
                'text': f"📸 ফর্ম সাবমিশন\nনাম: {name}\nUser ID: {user_id}\nছবি আপলোড করা হয়েছে",
                'parse_mode': 'HTML'
            }
            send_to_telegram_api('sendMessage', text_data)
        
        # Prepare success message for user
        if group_result:
            success_text = f"""
🎉 <b>ফর্ম সফলভাবে জমা হয়েছে!</b>

✅ <b>আপনার তথ্য:</b>
┣ <b>নাম:</b> {name}
┣ <b>ছবি:</b> ✅ আপলোডেড
┗ <b>গ্রুপ:</b> {GROUP_ID}

📊 <b>আপনার তথ্য গ্রুপে শেয়ার করা হয়েছে</b>

ধন্যবাদ! আপনার ফর্ম সাবমিশন সম্পূর্ণ হয়েছে।
            """
        else:
            success_text = f"""
⚠️ <b>ফর্ম জমা হয়েছে কিন্তু গ্রুপে পাঠানো যায়নি!</b>

✅ <b>আপনার তথ্য:</b>
┣ <b>নাম:</b> {name}
┣ <b>ছবি:</b> ✅ আপলোডেড

❌ <b>গ্রুপ:</b> {GROUP_ID} (পাঠানো যায়নি)

দয়া করে আবার চেষ্টা করুন।
            """
        
        # Clear session
        del SESSIONS[user_id]
        
        # Send success message to user
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': success_text,
            'parse_mode': 'HTML'
        })
        
    except Exception as e:
        # Clear session on error
        if user_id in SESSIONS:
            del SESSIONS[user_id]
        
        error_text = f"""
❌ <b>ফর্ম জমা দিতে সমস্যা!</b>

<code>ত্রুটি: {str(e)}</code>

দয়া করে আবার চেষ্টা করুন: /form
        """
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': error_text,
            'parse_mode': 'HTML'
        })

# Utility functions
def send_telegram_message(chat_id, text, parse_mode='HTML'):
    """Send message to Telegram"""
    return {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }

def send_telegram_photo(chat_id, photo_file_id, caption, parse_mode='HTML'):
    """Send photo to Telegram"""
    return {
        'method': 'sendPhoto',
        'chat_id': chat_id,
        'photo': photo_file_id,
        'caption': caption,
        'parse_mode': parse_mode
    }

def get_current_time():
    """Get current time string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_in_session(message, expected_command=None):
    """Check if user has active session"""
    user_id = message.get('from', {}).get('id')
    if user_id in SESSIONS:
        if expected_command:
            return SESSIONS[user_id].get('command') == expected_command
        return True
    return False

# Callback handler for menu integration
def handle_all_callbacks(callback_data, user_info, chat_id, message_id):
    """Handle form-related callbacks"""
    if callback_data == 'start_form':
        return handle_form(user_info, chat_id, "")
    return None
