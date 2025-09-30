import os
import requests
import telebot
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, jsonify
import logging

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ডিফল্ট টোকেন
DEFAULT_TOKEN = "7628222622:AAEomk7Od-jcKnQMdkmOpejvYYF47BjMAMQ"

# টোকেন লোড করার ফাংশন
def get_bot_token():
    # URL parameter থেকে টোকেন নিন
    token_from_url = request.args.get('token') if request else None
    if token_from_url:
        logger.info("✅ Token loaded from URL parameter")
        return token_from_url
    
    # ডিফল্ট টোকেন ব্যবহার করুন
    logger.info("✅ Using default token")
    return DEFAULT_TOKEN

# বট ইনিশিয়ালাইজেশন
def initialize_bot(token):
    try:
        bot = telebot.TeleBot(token)
        logger.info("✅ Bot initialized successfully")
        return bot
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        return None

# ইউটিউব ভিডিও আইডি এক্সট্র্যাক্ট করার ফাংশন
def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        if parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        if parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    return None

# থাম্বনেইল ডাউনলোড করার ফাংশন
def download_thumbnail(video_id):
    try:
        # বিভিন্ন রেজোলিউশনের থাম্বনেইল URL
        thumbnails = {
            'maxres': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'sd': f'https://img.youtube.com/vi/{video_id}/sddefault.jpg',
            'hq': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
            'mq': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
            'default': f'https://img.youtube.com/vi/{video_id}/default.jpg'
        }
        
        # সর্বোচ্চ কোয়ালিটির থাম্বনেইল ডাউনলোড করার চেষ্টা করুন
        for quality, url in thumbnails.items():
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                filename = f"{video_id}_{quality}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return filename
        return None
    except Exception as e:
        logger.error(f"Error downloading thumbnail: {e}")
        return None

# মেসেজ প্রসেস করার ফাংশন
def process_message(bot, message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    if text.startswith('/start'):
        welcome_text = """
🎉 **ইউটিউব থাম্বনেইল ডাউনলোডার বটে স্বাগতম!** 🎉

একটি ইউটিউব ভিডিওর লিংক পাঠান এবং আমি তার থাম্বনেইল ডাউনলোড করে দিব।

📌 **নির্দেশনা:**
1. একটি ইউটিউব ভিডিওর লিংক কপি করুন
2. লিংকটি এই চ্যাটে পাঠান
3. আমি থাম্বনেইল ডাউনলোড করে আপনাকে পাঠাব

উদাহরণ: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
        """
        bot.send_message(chat_id, welcome_text)
        return

    elif text.startswith('/help'):
        help_text = """
🤖 **ইউটিউব থাম্বনেইল ডাউনলোডার বট - সাহায্য**

📋 **কমান্ডসমূহ:**
/start - বট শুরু করুন
/help - এই সাহায্য মেসেজ দেখুন
/status - বট স্ট্যাটাস চেক করুন

🔗 **লিংক ফরম্যাট:**
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://www.youtube.com/embed/VIDEO_ID
        """
        bot.send_message(chat_id, help_text)
        return

    elif text.startswith('/status'):
        status_text = """
🤖 **বট স্ট্যাটাস**
✅ বট এক্টিভ এবং কাজ করছে
🖼️ ইউটিউব থাম্বনেইল ডাউনলোড করতে প্রস্তুত
🌐 Webhook মোড - অন-ডিমান্ড কাজ করে
        """
        bot.send_message(chat_id, status_text)
        return

    # ইউটিউব লিংক প্রসেস করা
    elif 'youtube.com' in text or 'youtu.be' in text:
        bot.send_message(chat_id, "🔍 আপনার ইউটিউব লিংক প্রসেস করা হচ্ছে...")
        
        video_id = extract_video_id(text)
        
        if video_id:
            try:
                yt = YouTube(text)
                video_title = yt.title
                
                bot.send_message(chat_id, f"📹 **ভিডিও টাইটেল:** {video_title}\n\n⬇️ থাম্বনেইল ডাউনলোড করা হচ্ছে...")
                
                thumbnail_file = download_thumbnail(video_id)
                
                if thumbnail_file:
                    with open(thumbnail_file, 'rb') as photo:
                        bot.send_photo(chat_id, photo, 
                                     caption=f"🖼️ **থাম্বনেইল ডাউনলোড সম্পূর্ণ!**\n\n📹 **ভিডিও:** {video_title}\n🔗 **ভিডিও আইডি:** `{video_id}`")
                    
                    os.remove(thumbnail_file)
                    logger.info(f"✅ Thumbnail sent for video: {video_id}")
                else:
                    bot.send_message(chat_id, "❌ থাম্বনেইল ডাউনলোড করতে সমস্যা হয়েছে। ভিডিওটি পাবলিক কিনা চেক করুন।")
                    
            except Exception as e:
                error_msg = f"❌ ভিডিও তথ্য পাওয়া যায়নি। ত্রুটি: {str(e)}"
                bot.send_message(chat_id, error_msg)
                logger.error(f"Video error: {e}")
        else:
            bot.send_message(chat_id, "❌ ভ্যালিড ইউটিউব লিংক প্রদান করুন।")
    else:
        bot.send_message(chat_id, "❌ দয়া করে একটি ভ্যালিড ইউটিউব লিংক পাঠান।")

# Flask Routes
@app.route('/')
def home():
    return jsonify({
        "status": "active", 
        "bot": "YouTube Thumbnail Downloader",
        "mode": "webhook",
        "description": "Bot works on-demand via webhook, not always connected",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/health",
            "set_webhook": "/set-webhook?url=YOUR_URL"
        },
        "usage": "Send Telegram messages to this bot, they will be processed via webhook"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mode": "webhook"})

@app.route('/set-webhook', methods=['GET', 'POST'])
def set_webhook():
    token = get_bot_token()
    bot = initialize_bot(token)
    
    if not bot:
        return jsonify({"status": "error", "message": "Failed to initialize bot"}), 500
    
    # Webhook URL - বর্তমান URL ব্যবহার করুন
    webhook_url = request.args.get('url') or request.url_root + 'webhook'
    
    try:
        # Telegram এ webhook সেট করুন
        result = bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        
        return jsonify({
            "status": "success", 
            "message": "Webhook set successfully",
            "webhook_url": webhook_url,
            "result": result
        })
    except Exception as e:
        logger.error(f"Webhook setting error: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Failed to set webhook: {str(e)}"
        }), 500

@app.route('/remove-webhook', methods=['GET', 'POST'])
def remove_webhook():
    token = get_bot_token()
    bot = initialize_bot(token)
    
    if not bot:
        return jsonify({"status": "error", "message": "Failed to initialize bot"}), 500
    
    try:
        # Webhook রিমুভ করুন
        result = bot.remove_webhook()
        logger.info("Webhook removed successfully")
        
        return jsonify({
            "status": "success", 
            "message": "Webhook removed successfully",
            "result": result
        })
    except Exception as e:
        logger.error(f"Webhook removal error: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Failed to remove webhook: {str(e)}"
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Telegram webhook endpoint - এখানে সব মেসেজ আসবে
    """
    if request.method == 'POST':
        try:
            # JSON ডেটা পান
            json_data = request.get_json()
            logger.info(f"📨 Received webhook data: {json_data}")
            
            if not json_data:
                return 'No data received', 400
            
            # টোকেন লোড করুন
            token = get_bot_token()
            bot = initialize_bot(token)
            
            if not bot:
                return 'Bot initialization failed', 500
            
            # Telegram update object তৈরি করুন
            update = telebot.types.Update.de_json(json_data)
            
            # মেসেজ থাকলে প্রসেস করুন
            if update.message:
                process_message(bot, update.message)
            
            return 'OK', 200
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return 'ERROR', 500

@app.route('/test', methods=['GET', 'POST'])
def test_bot():
    """
    টেস্ট এন্ডপয়েন্ট - ম্যানুয়ালি টেস্ট করার জন্য
    """
    token = get_bot_token()
    bot = initialize_bot(token)
    
    if not bot:
        return jsonify({"status": "error", "message": "Bot initialization failed"})
    
    # একটি টেস্ট মেসেজ সিমুলেট করুন
    class TestMessage:
        def __init__(self, text):
            self.chat = type('Chat', (), {'id': 123456})()  # ডামি chat ID
            self.text = text
    
    test_message = TestMessage("/start")
    process_message(bot, test_message)
    
    return jsonify({
        "status": "success", 
        "message": "Test message processed",
        "test_message": "/start"
    })

# মেইন এন্ট্রি পয়েন্ট
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting YouTube Thumbnail Bot on port {port}")
    logger.info("🌐 Webhook Mode - Bot will work on-demand only")
    
    # Flask app চালু করুন
    app.run(host='0.0.0.0', port=port, debug=False)
