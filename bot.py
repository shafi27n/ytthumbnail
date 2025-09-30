from flask import Flask, request, jsonify
import requests
import re
import os
import logging
from urllib.parse import urlparse, parse_qs

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
            r'(?:youtube\.com\/watch\?v=||youtu\.be\/||youtube\.com\/embed\/)([^&=\n?\s]+)',
            r'youtube\.com\/watch\?.*v=([^&=\n?\s]+)',
            r'youtu\.be\/([^&=\n?\s]+)'
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

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    try:
        # URL থেকে টোকেন নেওয়া
        token = request.args.get('token')
        
        if not token:
            return jsonify({
                'error': 'টোকেন প্রয়োজন',
                'solution': 'URL এ ?token=YOUR_BOT_TOKEN যোগ করুন'
            }), 400
        
        # GET request হ্যান্ডেল
        if request.method == 'GET':
            return jsonify({
                'status': 'বট একটিভ',
                'instruction': 'POST request এর মাধ্যমে YouTube লিংক সেন্ড করুন',
                'usage': 'টেলিগ্রাম বটের ওয়েবহুক URL: https://your-domain.com/?token=YOUR_BOT_TOKEN'
            })
        
        # POST request হ্যান্ডেল
        if request.method == 'POST':
            update = request.get_json()
            
            if not update:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # মেসেজ ডেটা এক্সট্র্যাক্ট
            chat_id = None
            message_text = ''
            message_id = None
            
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                message_text = update['message'].get('text', '')
                message_id = update['message'].get('message_id')
            elif 'channel_post' in update:
                chat_id = update['channel_post']['chat']['id']
                message_text = update['channel_post'].get('text', '')
                message_id = update['channel_post'].get('message_id')
            elif 'callback_query' in update:
                # Callback query হ্যান্ডেল (যদি ইনলাইন বাটন ব্যবহার করেন)
                chat_id = update['callback_query']['message']['chat']['id']
                message_id = update['callback_query']['message']['message_id']
                return jsonify({
                    'method': 'answerCallbackQuery',
                    'callback_query_id': update['callback_query']['id'],
                    'text': 'Processing...'
                })
            
            if not chat_id:
                return jsonify({'error': 'চ্যাট আইডি পাওয়া যায়নি'}), 400
            
            # /start কমান্ড হ্যান্ডেল
            if message_text.startswith('/start'):
                welcome_text = f"""
🌟 <b>স্বাগতম YouTube Thumbnail Downloader Bot এ!</b> 🌟

<b>ব্যবহার বিধি:</b>
1. যেকোনো YouTube ভিডিওর লিংক সেন্ড করুন
2. বট স্বয়ংক্রিয়ভাবে সবগুলো থাম্বনেইল দেখাবে
3. আপনার পছন্দমত থাম্বনেইল সিলেক্ট করুন

<b>সাপোর্টেড লিংক ফরম্যাট:</b>
• https://youtube.com/watch?v=VIDEO_ID
• https://youtu.be/VIDEO_ID
• https://www.youtube.com/embed/VIDEO_ID

<b>কমান্ডস:</b>
/start - এই মেসেজ দেখাবে
/help - সাহায্য পেতে

<b>উদাহরণ:</b>
https://youtu.be/dQw4w9WgXcQ
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
            
            # YouTube লিংক প্রসেস
            else:
                # YouTube লিংক চেক
                youtube_patterns = [
                    r'youtube\.com/watch\?v=',
                    r'youtu\.be/',
                    r'youtube\.com/embed/'
                ]
                
                is_youtube_link = any(pattern in message_text for pattern in youtube_patterns)
                
                if is_youtube_link:
                    # থাম্বনেইল এক্সট্র্যাক্ট
                    thumbnails, error = extract_youtube_thumbnail(message_text)
                    
                    if error:
                        return jsonify({
                            'method': 'sendMessage',
                            'chat_id': chat_id,
                            'text': f"❌ {error}",
                            'parse_mode': 'HTML'
                        })
                    
                    # থাম্বনেইল বাটন সহ মেসেজ সেন্ড
                    buttons = []
                    for quality, thumb_url in thumbnails.items():
                        buttons.append([
                            {
                                'text': f"📷 {quality.upper()} কোয়ালিটি",
                                'url': thumb_url
                            }
                        ])
                    
                    # সবগুলো থাম্বনেইল দেখানোর জন্য বাটন
                    reply_markup = {'inline_keyboard': buttons}
                    
                    response_text = f"""
<b>✅ থাম্বনেইল পাওয়া গেছে!</b>

<b>ভিডিও লিংক:</b> {message_text}

<b>থাম্বনেইল গুলো:</b>
• <b>Default</b> - ছোট সাইজ (120×90)
• <b>Medium</b> - মধ্যম কোয়ালিটি (320×180)  
• <b>High</b> - উচ্চ কোয়ালিটি (480×360)
• <b>Standard</b> - স্ট্যান্ডার্ড ডেফিনিশন (640×480)
• <b>Max Resolution</b> - সর্বোচ্চ রেজোলিউশন (1280×720)

<b>নিচের বাটন থেকে আপনার পছন্দের থাম্বনেইল সিলেক্ট করুন:</b>
                    """
                    
                    # প্রথম থাম্বনেইল প্রিভিউ হিসেবে সেন্ড
                    preview_thumb = thumbnails.get('high', thumbnails['default'])
                    
                    return jsonify({
                        'method': 'sendPhoto',
                        'chat_id': chat_id,
                        'photo': preview_thumb,
                        'caption': response_text,
                        'parse_mode': 'HTML',
                        'reply_markup': reply_markup
                    })
                
                else:
                    # যদি YouTube লিংক না হয়
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
                        """,
                        'parse_mode': 'HTML'
                    })
    
    except Exception as e:
        logger.error(f'Global error: {e}')
        return jsonify({
            'error': 'প্রসেসিং ব্যর্থ',
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'service': 'YouTube Thumbnail Bot'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Production server ব্যবহার করুন
    app.run(host='0.0.0.0', port=port)
