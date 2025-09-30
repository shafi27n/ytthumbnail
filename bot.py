from flask import Flask, request, jsonify
import requests
import re
import os
import logging
import base64
from io import BytesIO

# লগিং কনফিগারেশন
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def extract_youtube_thumbnail(video_url):
    """
    YouTube ভিডিও URL থেকে থাম্বনেইল লিংক বের করে
    """
    try:
        # ভিডিও ID এক্সট্র্যাক্ট
        video_id = None
        
        # বিভিন্ন YouTube URL ফরম্যাট হ্যান্ডেল করা
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id:
            return None, "ভালিড YouTube লিংক প্রদান করুন।"
        
        # বিভিন্ন কোয়ালিটির থাম্বনেইল URLs
        thumbnails = {
            'default': f'https://img.youtube.com/vi/{video_id}/default.jpg',
            'medium': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
            'high': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
            'standard': f'https://img.youtube.com/vi/{video_id}/sddefault.jpg',
            'maxres': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
        }
        
        return thumbnails, None
        
    except Exception as e:
        logger.error(f"Thumbnail extraction error: {e}")
        return None, f"ত্রুটি: {str(e)}"

def is_youtube_url(text):
    """চেক করে দেখে টেক্সট YouTube URL কিনা"""
    youtube_patterns = [
        r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)[a-zA-Z0-9_-]{11}',
        r'youtube\.com/watch\?.*v=[a-zA-Z0-9_-]{11}',
    ]
    
    for pattern in youtube_patterns:
        if re.search(pattern, text):
            return True
    return False

def download_image(image_url):
    """
    ইমেজ URL থেকে ডেটা ডাউনলোড করে
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, timeout=10, headers=headers)
        response.raise_for_status()
        return response.content, None
    except Exception as e:
        logger.error(f"Image download error: {e}")
        return None, f"ইমেজ ডাউনলোড করতে সমস্যা: {str(e)}"

def send_telegram_photo(chat_id, photo_url, caption, reply_markup=None, reply_to_message_id=None):
    """
    Telegram-এ ফটো সেন্ড করার জন্য সহায়ক ফাংশন
    """
    return {
        'method': 'sendPhoto',
        'chat_id': chat_id,
        'photo': photo_url,  # সরাসরি URL ব্যবহার করি
        'caption': caption,
        'parse_mode': 'Markdown',
        'reply_markup': reply_markup,
        'reply_to_message_id': reply_to_message_id
    }

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
                'status': 'Bot is running',
                'token_received': True,
                'message': 'YouTube Thumbnail Downloader Bot is ready!'
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
                
                # ক্যালব্যাক ডেটা পার্স করা (format: quality|video_id)
                if '|' in data:
                    quality, video_id = data.split('|', 1)
                    
                    # কোয়ালিটির নাম
                    quality_names = {
                        'default': {'name': 'ছোট', 'emoji': '🟢', 'size': '120×90'},
                        'medium': {'name': 'মধ্যম', 'emoji': '🟡', 'size': '320×180'}, 
                        'high': {'name': 'বড়', 'emoji': '🟠', 'size': '480×360'},
                        'standard': {'name': 'স্ট্যান্ডার্ড', 'emoji': '🔵', 'size': '640×480'},
                        'maxres': {'name': 'সর্বোচ্চ', 'emoji': '🔴', 'size': '1280×720'}
                    }
                    
                    quality_info = quality_names.get(quality, {'name': quality, 'emoji': '📷', 'size': 'Unknown'})
                    thumbnail_url = f'https://img.youtube.com/vi/{video_id}/{quality}.jpg'
                    
                    # প্রথমে ক্যালব্যাক কুয়েরি উত্তর দেই
                    responses = [
                        answer_callback_query(callback_query_id, f"{quality_info['emoji']} {quality_info['name']} কোয়ালিটি থাম্বনেইল প্রস্তুত হচ্ছে...", False)
                    ]
                    
                    # তারপর ফটো সেন্ড করি
                    caption = f"""🖼️ **{quality_info['emoji']} {quality_info['name']} কোয়ালিটি থাম্বনেইল**

📏 **রেজোলিউশন:** `{quality_info['size']}`
🎯 **কোয়ালিটি:** `{quality}`
🆔 **ভিডিও আইডি:** `{video_id}`

✅ **থাম্বনেইল সফলভাবে ডাউনলোড হয়েছে!**"""
                    
                    responses.append(
                        send_telegram_photo(
                            chat_id=chat_id,
                            photo_url=thumbnail_url,
                            caption=caption,
                            reply_to_message_id=message_id
                        )
                    )
                    
                    return jsonify(responses) if len(responses) > 1 else jsonify(responses[0])
                
                return jsonify(answer_callback_query(callback_query_id, "ইনভ্যালিড রিকোয়েস্ট", True))
            
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

            # /start কমান্ড হ্যান্ডেল
            if message_text.startswith('/start'):
                welcome_text = """
🎬 **স্বাগতম YouTube Thumbnail Downloader Bot এ!** 🎬

📥 **ব্যবহার বিধি:**
1. যেকোনো YouTube ভিডিওর লিংক সেন্ড করুন
2. বট স্বয়ংক্রিয়ভাবে সবগুলো থাম্বনেইল অপশন দেখাবে
3. আপনার পছন্দমত থাম্বনেইল সিলেক্ট করুন

🔗 **সাপোর্টেড লিংক ফরম্যাট:**
• `https://youtube.com/watch?v=VIDEO_ID`
• `https://youtu.be/VIDEO_ID`  
• `https://www.youtube.com/embed/VIDEO_ID`

📋 **উদাহরণ:**
`https://youtu.be/dQw4w9WgXcQ`
`https://www.youtube.com/watch?v=dQw4w9WgXcQ`

👉 **এখনই একটি YouTube লিংক সেন্ড করে ট্রাই করুন!**
                """
                
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=welcome_text,
                    disable_web_page_preview=True
                ))

            # /help কমান্ড হ্যান্ডেল
            elif message_text.startswith('/help'):
                help_text = """
🆘 **সাহায্য:** 🆘

এই বট YouTube ভিডিও থেকে হাই-কোয়ালিটি থাম্বনেইল ডাউনলোড করতে সাহায্য করে।

📖 **কিভাবে ব্যবহার করবেন:**
1. YouTube ভিডিওর লিংক কপি করুন
2. বটে পেস্ট করুন
3. বিভিন্ন কোয়ালিটির থাম্বনেইল দেখুন
4. আপনার পছন্দের থাম্বনেইল সিলেক্ট করুন

🎯 **কোয়ালিটি অপশন:**
• 🟢 ছোট (120×90)
• 🟡 মধ্যম (320×180) 
• 🟠 বড় (480×360)
• 🔵 স্ট্যান্ডার্ড (640×480)
• 🔴 সর্বোচ্চ (1280×720)

⚠️ **সমস্যা হলে:**
• লিংকটি চেক করুন
• নেটওয়ার্ক কানেকশন চেক করুন
• আবার চেষ্টা করুন

🛠️ **সাপোর্ট:** সমস্যা হলে /start কমান্ড দিয়ে আবার শুরু করুন।
                """
                
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text=help_text
                ))

            # YouTube লিংক চেক
            elif is_youtube_url(message_text):
                # থাম্বনেইল এক্সট্র্যাক্ট
                thumbnails, error = extract_youtube_thumbnail(message_text)
                
                if error:
                    return jsonify(send_telegram_message(
                        chat_id=chat_id,
                        text=f"❌ {error}"
                    ))
                
                # ভিডিও ID এক্সট্র্যাক্ট
                video_id = None
                patterns = [
                    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, message_text)
                    if match:
                        video_id = match.group(1)
                        break
                
                if not video_id:
                    return jsonify(send_telegram_message(
                        chat_id=chat_id,
                        text="❌ ভিডিও ID খুঁজে পাওয়া যায়নি।"
                    ))
                
                # ইনলাইন বাটন তৈরি
                buttons = []
                row = []
                
                quality_info = {
                    'default': {'name': 'ছোট', 'emoji': '🟢'},
                    'medium': {'name': 'মধ্যম', 'emoji': '🟡'},
                    'high': {'name': 'বড়', 'emoji': '🟠'},
                    'standard': {'name': 'স্ট্যান্ডার্ড', 'emoji': '🔵'},
                    'maxres': {'name': 'সর্বোচ্চ', 'emoji': '🔴'}
                }
                
                for i, quality in enumerate(['default', 'medium', 'high', 'standard', 'maxres']):
                    if quality in thumbnails:
                        quality_data = quality_info[quality]
                        row.append({
                            'text': f"{quality_data['emoji']} {quality_data['name']}",
                            'callback_data': f"{quality}|{video_id}"
                        })
                        
                        # প্রতি row এ 2টি বাটন
                        if len(row) == 2:
                            buttons.append(row)
                            row = []
                
                # শেষ row যোগ করুন
                if row:
                    buttons.append(row)
                
                reply_markup = {'inline_keyboard': buttons}
                
                response_text = f"""
✅ **থাম্বনেইল পাওয়া গেছে!**

📹 **ভিডিও লিংক:**
`{message_text}`

🎯 **উপলব্ধ থাম্বনেইল কোয়ালিটি:**
• 🟢 ছোট (120×90) - ডিফল্ট
• 🟡 মধ্যম (320×180) - মধ্যম কোয়ালিটি  
• 🟠 বড় (480×360) - হাই কোয়ালিটি
• 🔵 স্ট্যান্ডার্ড (640×480) - SD কোয়ালিটি
• 🔴 সর্বোচ্চ (1280×720) - HD কোয়ালিটি

👇 **নিচের বাটন থেকে আপনার পছন্দের থাম্বনেইল সিলেক্ট করুন:**
                """
                
                # সর্বোচ্চ কোয়ালিটির থাম্বনেইল প্রিভিউ হিসেবে সেন্ড
                preview_thumb = thumbnails.get('maxres', 
                              thumbnails.get('standard', 
                              thumbnails.get('high', 
                              list(thumbnails.values())[0])))
                
                return jsonify(send_telegram_photo(
                    chat_id=chat_id,
                    photo_url=preview_thumb,
                    caption=response_text,
                    reply_markup=reply_markup
                ))

            # যদি YouTube লিংক না হয়
            else:
                return jsonify(send_telegram_message(
                    chat_id=chat_id,
                    text="""
❌ **ইনভ্যালিড লিংক**

দয়া করে একটি বৈধ YouTube লিংক সেন্ড করুন।

🔗 **সাপোর্টেড ফরম্যাট:**
• `https://youtube.com/watch?v=VIDEO_ID`
• `https://youtu.be/VIDEO_ID`
• `https://www.youtube.com/embed/VIDEO_ID`

📋 **উদাহরণ:**
`https://youtu.be/dQw4w9WgXcQ`
`https://www.youtube.com/watch?v=dQw4w9WgXcQ`

💡 **সাহায্যের জন্য** `/help` কমান্ড ব্যবহার করুন।
                    """,
                    disable_web_page_preview=True
                ))
    
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
            'status': 'Bot is running',
            'token_received': True,
            'endpoint': path
        })
    
    # POST request এর জন্য মূল লজিকে redirect
    return handle_request()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
