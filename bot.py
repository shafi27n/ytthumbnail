import os
import requests
import telebot
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, jsonify

app = Flask(__name__)

# Webhook URL থেকে টোকেন এক্সট্র্যাক্ট করার ফাংশন
def get_token_from_webhook():
    webhook_url = os.environ.get('WEBHOOK_URL', '')
    if webhook_url:
        try:
            parsed_url = urlparse(webhook_url)
            query_params = parse_qs(parsed_url.query)
            token = query_params.get('token', [None])[0]
            return token
        except:
            return None
    return None

# টোকেন লোড করুন
BOT_TOKEN = get_token_from_webhook()

if not BOT_TOKEN:
    # যদি Webhook থেকে টোকেন না মেলে, environment variable থেকে চেষ্টা করুন
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    
if not BOT_TOKEN:
    raise ValueError("❌ বট টোকেন পাওয়া যায়নি। WEBHOOK_URL বা BOT_TOKEN environment variable সেট করুন।")

bot = telebot.TeleBot(BOT_TOKEN)

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
            if response.status_code == 200 and len(response.content) > 1000:  # ভ্যালিড ইমেজ চেক
                filename = f"{video_id}_{quality}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return filename
        return None
    except Exception as e:
        print(f"Error downloading thumbnail: {e}")
        return None

# /start কমান্ড হ্যান্ডলার
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

# /help কমান্ড হ্যান্ডলার
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

❓ **সমস্যা সমাধান:**
- ভ্যালিড ইউটিউব লিংক পাঠান নিশ্চিত করুন
- লিংকটি পাবলিক ভিডিওর হতে হবে
- ইন্টারনেট কানেকশন চেক করুন
    """
    bot.reply_to(message, help_text)

# ইউটিউব লিংক প্রসেস করার হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_youtube_link(message):
    text = message.text.strip()
    
    # চেক করুন যদি মেসেজে ইউটিউব লিংক থাকে
    if 'youtube.com' in text or 'youtu.be' in text:
        bot.reply_to(message, "🔍 আপনার ইউটিউব লিংক প্রসেস করা হচ্ছে...")
        
        video_id = extract_video_id(text)
        
        if video_id:
            try:
                # ভিডিও তথ্য পাওয়ার জন্য pytube ব্যবহার
                yt = YouTube(text)
                video_title = yt.title
                
                bot.reply_to(message, f"📹 **ভিডিও টাইটেল:** {video_title}\n\n⬇️ থাম্বনেইল ডাউনলোড করা হচ্ছে...")
                
                # থাম্বনেইল ডাউনলোড করুন
                thumbnail_file = download_thumbnail(video_id)
                
                if thumbnail_file:
                    # থাম্বনেইল ফাইল পাঠান
                    with open(thumbnail_file, 'rb') as photo:
                        bot.send_photo(message.chat.id, photo, 
                                     caption=f"🖼️ **থাম্বনেইল ডাউনলোড সম্পূর্ণ!**\n\n📹 **ভিডিও:** {video_title}\n🔗 **ভিডিও আইডি:** `{video_id}`")
                    
                    # টেম্পোরারি ফাইল ডিলিট করুন
                    os.remove(thumbnail_file)
                else:
                    bot.reply_to(message, "❌ থাম্বনেইল ডাউনলোড করতে সমস্যা হয়েছে। ভিডিওটি পাবলিক কিনা চেক করুন।")
                    
            except Exception as e:
                bot.reply_to(message, f"❌ ভিডিও তথ্য পাওয়া যায়নি। ত্রুটি: {str(e)}")
        else:
            bot.reply_to(message, "❌ ভ্যালিড ইউটিউব লিংক প্রদান করুন।")
    else:
        bot.reply_to(message, "❌ দয়া করে একটি ভ্যালিড ইউটিউব লিংক পাঠান।")

# Webhook endpoint for health check
@app.route('/')
def home():
    return jsonify({
        "status": "active", 
        "bot": "YouTube Thumbnail Downloader",
        "token_received": bool(BOT_TOKEN)
    })

# Webhook endpoint for receiving updates (optional)
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200

# Polling মেথড দিয়ে বট চালু (শেয়ার্ড হোস্টিং এর জন্য উপযোগী)
if __name__ == "__main__":
    print("🤖 বট চালু হয়েছে...")
    print(f"🔑 টোকেন স্ট্যাটাস: {'✅ পাওয়া গেছে' if BOT_TOKEN else '❌ পাওয়া যায়নি'}")
    
    # Environment variables থেকে ওয়েবহুক URL প্রিন্ট করুন
    webhook_url = os.environ.get('WEBHOOK_URL', 'Not set')
    print(f"🌐 Webhook URL: {webhook_url}")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ বট চালু করতে সমস্যা: {e}")
