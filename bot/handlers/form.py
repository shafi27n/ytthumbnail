import requests
import json
from flask import jsonify
from datetime import datetime

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

def process_form_completion(user_id, chat_id):
    """Process completed form and send to group"""
    try:
        user_data = SESSIONS[user_id]['data']
        name = user_data.get('name', 'N/A')
        photo_file_id = user_data.get('photo_file_id')
        user_info = user_data.get('user_info', {})
        
        # Group ID - REPLACE WITH YOUR ACTUAL GROUP ID
        GROUP_ID = "@refffrrr"  # Change this to your actual group username or ID
        
        # Prepare message for group
        group_message = f"""
📋 <b>নতুন ফর্ম সাবমিশন</b>

👤 <b>ব্যবহারকারী:</b> {user_info.get('first_name', 'N/A')}
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>নাম:</b> {name}
📅 <b>সময়:</b> {get_current_time()}

✅ ফর্ম সম্পূর্ণ হয়েছে!
        """
        
        # Send photo with caption to group
        group_response = {
            'method': 'sendPhoto',
            'chat_id': GROUP_ID,
            'photo': photo_file_id,
            'caption': group_message,
            'parse_mode': 'HTML'
        }
        
        # Prepare success message for user
        success_text = f"""
🎉 <b>ফর্ম সফলভাবে জমা হয়েছে!</b>

✅ <b>আপনার তথ্য:</b>
┣ <b>নাম:</b> {name}
┣ <b>ছবি:</b> ✅ আপলোডেড
┗ <b>গ্রুপ:</b> {GROUP_ID}

📊 <b>আপনার তথ্য গ্রুপে শেয়ার করা হয়েছে</b>

ধন্যবাদ! আপনার ফর্ম সাবমিশন সম্পূর্ণ হয়েছে।
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
