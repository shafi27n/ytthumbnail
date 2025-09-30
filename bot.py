from flask import Flask, request, jsonify
import requests
import re
import os
import logging

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
                'message': 'Webhook is set up correctly'
            })

        # POST request হ্যান্ডেল - টেলিগ্রাম আপডেট
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
🌟 <b>স্বাগতম YouTube Thumbnail Downloader Bot এ!</b> 🌟

<b>ব্যবহার বিধি:</b>
1. যেকোনো YouTube ভিডিওর লিংক সেন্ড করুন
2. বট স্বয়ংক্রিয়ভাবে সবগুলো থাম্বনেইল দেখাবে
3. আপনার পছন্দমত থাম্বনেইল সিলেক্ট করুন

<b>সাপোর্টেড লিংক ফরম্যাট:</b>
• https://youtube.com/watch?v=VIDEO_ID
• https://youtu.be/VIDEO_ID  
• https://www.youtube.com/embed/VIDEO_ID

<b>উদাহরণ:</b>
<code>https://youtu.be/dQw4w9WgXcQ</code>
<code>https://www.youtube.com/watch?v=dQw4w9WgXcQ</code>
                """
                
                return jsonify({
                    'method': 'sendMessage',
                    'chat_id': chat_id,
                    'text': welcome_text,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                })

            # /help কমান্ড হ্যান্ডেল
            elif message_text.startswith('/help'):
                help_text = """
<b>সাহায্য:</b>
এই বট YouTube ভিডিও থেকে হাই-কোয়ালিটি থাম্বনেইল ডাউনলোড করতে সাহায্য করে।

<b>কিভাবে ব্যবহার করবেন:</b>
1. YouTube ভিডিওর লিংক কপি করুন
2. বটে পেস্ট করুন
3. বিভিন্ন কোয়ালিটির থাম্বনেইল দেখুন
4. আপনার পছন্দের থাম্বনেইল ডাউনলোড করুন

<b>সমস্যা হলে:</b>
• লিংকটি চেক করুন
• নেটওয়ার্ক কানেকশন চেক করুন
• আবার চেষ্টা করুন
                """
                
                return jsonify({
                    'method': 'sendMessage',
                    'chat_id': chat_id,
                    'text': help_text,
                    'parse_mode': 'HTML'
                })

            # YouTube লিংক চেক
            elif is_youtube_url(message_text):
                # থাম্বনেইল এক্সট্র্যাক্ট
                thumbnails, error = extract_youtube_thumbnail(message_text)
                
                if error:
                    return jsonify({
                        'method': 'sendMessage',
                        'chat_id': chat_id,
                        'text': f"❌ {error}",
                        'parse_mode': 'HTML'
                    })
                
                # থাম্বনেইল বাটন তৈরি
                buttons = []
                for quality, thumb_url in thumbnails.items():
                    quality_names = {
                        'default': 'ছোট',
                        'medium': 'মধ্যম', 
                        'high': 'বড়',
                        'standard': 'স্ট্যান্ডার্ড',
                        'maxres': 'সর্বোচ্চ'
                    }
                    quality_name = quality_names.get(quality, quality)
                    buttons.append([{
                        'text': f"📷 {quality_name} কোয়ালিটি",
                        'url': thumb_url
                    }])
                
                reply_markup = {'inline_keyboard': buttons}
                
                response_text = f"""
<b>✅ থাম্বনেইল পাওয়া গেছে!</b>

<b>ভিডিও লিংক:</b>
<code>{message_text}</code>

<b>উপলব্ধ থাম্বনেইল:</b>
{chr(10).join([f"• {quality_names.get(qual, qual)} কোয়ালিটি" for qual in thumbnails.keys()])}

<b>নিচের বাটন থেকে আপনার পছন্দের থাম্বনেইল সিলেক্ট করুন:</b>
                """
                
                # সর্বোচ্চ কোয়ালিটির থাম্বনেইল প্রিভিউ হিসেবে সেন্ড
                preview_thumb = thumbnails.get('maxres', 
                              thumbnails.get('standard', 
                              thumbnails.get('high', 
                              list(thumbnails.values())[0])))
                
                return jsonify({
                    'method': 'sendPhoto',
                    'chat_id': chat_id,
                    'photo': preview_thumb,
                    'caption': response_text,
                    'parse_mode': 'HTML',
                    'reply_markup': reply_markup
                })

            # যদি YouTube লিংক না হয়
            else:
                return jsonify({
                    'method': 'sendMessage',
                    'chat_id': chat_id,
                    'text': """
<b>❌ ইনভ্যালিড লিংক</b>

দয়া করে একটি বৈধ YouTube লিংক সেন্ড করুন।

<b>সাপোর্টেড ফরম্যাট:</b>
• https://youtube.com/watch?v=VIDEO_ID
• https://youtu.be/VIDEO_ID
• https://www.youtube.com/embed/VIDEO_ID

<b>উদাহরণ:</b>
<code>https://youtu.be/dQw4w9WgXcQ</code>
<code>https://www.youtube.com/watch?v=dQw4w9WgXcQ</code>
                    """,
                    'parse_mode': 'HTML'
                })
    
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
