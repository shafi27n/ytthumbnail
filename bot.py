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

# ডিফল্ট টোকেন - সরাসরি কোডে
DEFAULT_TOKEN = "7628222622:AAEomk7Od-jcKnQMdkmOpejvYYF47BjMAMQ"

# টোকেন লোড করার ফাংশন - URL parameter থেকে অথবা ডিফল্ট টোকেন ব্যবহার
def get_bot_token():
    # Flask request থেকে URL parameter চেক করুন
    token_from_url = request.args.get('token') if request else None
    if token_from_url:
        logger.info("✅ Token loaded from URL parameter")
        return token_from_url
    
    # ডিফল্ট টোকেন ব্যবহার করুন
    logger.info("✅ Using default token")
    return DEFAULT_TOKEN

# গ্লোবাল বট অবজেক্ট
bot = None

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

# বট ইনিশিয়ালাইজেশন ফাংশন
def initialize_bot(token):
    global bot
    try:
        bot = telebot.TeleBot(token)
        logger.info("✅ Bot initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        return False

# বট কমান্ড হ্যান্ডলার
def setup_bot_handlers():
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        welcome_text = """
🎉 **ইউটিউব থাম্বনেইল ডাউনলোডার বটে স্বাগতম!** 🎉

একটি ইউটিউব ভিডিওর লিংক পাঠান এবং আমি তার থাম্বনেইল ডাউনলোড করে দিব।

📌 **নির্দেশনা:**
1. একটি ইউটিউব ভিডিওর লিংক কপি করুন
2. লিংকটি এই চ্যাটে পাঠান
3. আমি থাম্বনেইল ডাউনলোড করে আপনাকে পাঠাব

উদাহরণ: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
        """
        bot.reply_to(message, welcome_text)

    @bot.message_handler(commands=['help'])
    def send_help(message):
        help_text = """
🤖 **ইউটিউব থাম্বনেইল ডাউনলোডার বট - সাহায্য**

📋 **কমান্ডসমূহ:**
/start - বট শুরু করুন
/help - এই সাহায্য মেসেজ দেখুন

🔗 **লিংক ফরম্যাট:**
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://www.youtube.com/embed/VIDEO_ID
        """
        bot.reply_to(message, help_text)

    @bot.message_handler(commands=['status'])
    def send_status(message):
        status_text = """
🤖 **বট স্ট্যাটাস**
✅ বট এক্টিভ এবং কাজ করছে
🖼️ ইউটিউব থাম্বনেইল ডাউনলোড করতে প্রস্তুত
        """
        bot.reply_to(message, status_text)

    @bot.message_handler(func=lambda message: True)
    def handle_youtube_link(message):
        text = message.text.strip()
        
        if 'youtube.com' in text or 'youtu.be' in text:
            bot.reply_to(message, "🔍 আপনার ইউটিউব লিংক প্রসেস করা হচ্ছে...")
            
            video_id = extract_video_id(text)
            
            if video_id:
                try:
                    yt = YouTube(text)
                    video_title = yt.title
                    
                    bot.reply_to(message, f"📹 **ভিডিও টাইটেল:** {video_title}\n\n⬇️ থাম্বনেইল ডাউনলোড করা হচ্ছে...")
                    
                    thumbnail_file = download_thumbnail(video_id)
                    
                    if thumbnail_file:
                        with open(thumbnail_file, 'rb') as photo:
                            bot.send_photo(message.chat.id, photo, 
                                         caption=f"🖼️ **থাম্বনেইল ডাউনলোড সম্পূর্ণ!**\n\n📹 **ভিডিও:** {video_title}\n🔗 **ভিডিও আইডি:** `{video_id}`")
                        
                        os.remove(thumbnail_file)
                        logger.info(f"✅ Thumbnail sent for video: {video_id}")
                    else:
                        bot.reply_to(message, "❌ থাম্বনেইল ডাউনলোড করতে সমস্যা হয়েছে। ভিডিওটি পাবলিক কিনা চেক করুন।")
                        
                except Exception as e:
                    error_msg = f"❌ ভিডিও তথ্য পাওয়া যায়নি। ত্রুটি: {str(e)}"
                    bot.reply_to(message, error_msg)
                    logger.error(f"Video error: {e}")
            else:
                bot.reply_to(message, "❌ ভ্যালিড ইউটিউব লিংক প্রদান করুন।")
        else:
            bot.reply_to(message, "❌ দয়া করে একটি ভ্যালিড ইউটিউব লিংক পাঠান।")

# Flask Routes
@app.route('/')
def home():
    token = get_bot_token()
    bot_initialized = initialize_bot(token) if token else False
    
    return jsonify({
        "status": "active", 
        "bot": "YouTube Thumbnail Downloader",
        "token_used": "default" if token == DEFAULT_TOKEN else "from_url",
        "bot_initialized": bot_initialized,
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "start_bot": "/start-bot"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot_running": bot is not None})

@app.route('/start-bot')
def start_bot():
    token = get_bot_token()
    if initialize_bot(token):
        setup_bot_handlers()
        
        # বট পোলিং শুরু করুন (background এ)
        import threading
        def start_polling():
            try:
                logger.info("🔄 Starting bot polling...")
                bot.infinity_polling()
            except Exception as e:
                logger.error(f"Bot polling error: {e}")
        
        bot_thread = threading.Thread(target=start_polling)
        bot_thread.daemon = True
        bot_thread.start()
        
        return jsonify({
            "status": "success", 
            "message": "Bot started successfully",
            "token_source": "default" if token == DEFAULT_TOKEN else "url_parameter"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "Failed to initialize bot"
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            
            # বট ইনিশিয়ালাইজ করা নেই就先 করুন
            token = get_bot_token()
            if not bot:
                initialize_bot(token)
                setup_bot_handlers()
            
            bot.process_new_updates([update])
            return 'OK', 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return 'ERROR', 500

# মেইন এন্ট্রি পয়েন্ট
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting YouTube Thumbnail Bot on port {port}")
    
    # অটোমেটিকভাবে বট শুরু করুন
    token = DEFAULT_TOKEN  # ডিফল্ট টোকেন ব্যবহার
    if initialize_bot(token):
        setup_bot_handlers()
        
        # বট পোলিং শুরু করুন
        import threading
        def start_polling():
            try:
                logger.info("🔄 Starting bot polling...")
                bot.infinity_polling()
            except Exception as e:
                logger.error(f"Bot polling error: {e}")
        
        bot_thread = threading.Thread(target=start_polling)
        bot_thread.daemon = True
        bot_thread.start()
    
    # Flask app চালু করুন
    app.run(host='0.0.0.0', port=port, debug=False)
