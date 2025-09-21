import telebot
from telebot import types
import requests
import os
import re
from flask import Flask, request

# ==== CONFIG ====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7628222622:AAEomk7Od-jcKnQMdkmOpejvYYF47BjMAMQ')
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# ==== YOUTUBE THUMBNAIL URL GENERATOR ====
def get_youtube_thumbnail(url):
    """Extract YouTube video ID and generate thumbnail URLs"""
    # Extract video ID from various YouTube URL formats
    video_id = None
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]+)',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]+)',
        r'youtu\.be\/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    
    if not video_id:
        return None
    
    # Generate thumbnail URLs in different qualities
    thumbnails = {
        'maxres': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
        'hq': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
        'mq': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
        'sd': f'https://img.youtube.com/vi/{video_id}/sddefault.jpg'
    }
    
    return thumbnails, video_id

# ==== FLASK ROUTES FOR WEBHOOK ====
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid content type', 403

@app.route('/')
def index():
    return 'YouTube Thumbnail Downloader Bot is running!'

# ==== BOT COMMAND HANDLERS ====
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = """
🎬 <b>YouTube Thumbnail Downloader Bot</b>

Send me a YouTube video URL and I'll download all available thumbnails for you!

📌 <b>How to use:</b>
1. Copy YouTube video URL
2. Send it to me
3. I'll show you all available thumbnails
4. Choose which one you want to download

🔗 <b>Supported URL formats:</b>
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://www.youtube.com/embed/VIDEO_ID

Try it now by sending a YouTube link!
"""
    bot.send_message(chat_id, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    # Check if the message contains a YouTube URL
    if 'youtube.com' in text or 'youtu.be' in text:
        bot.send_chat_action(chat_id, 'typing')
        
        # Get thumbnails
        result = get_youtube_thumbnail(text)
        
        if not result:
            bot.send_message(chat_id, "❌ <b>Invalid YouTube URL</b>\n\nPlease send a valid YouTube video URL.")
            return
        
        thumbnails, video_id = result
        
        # Send available thumbnails
        caption = f"📺 <b>Available Thumbnails for:</b>\n<code>{text}</code>\n\nChoose a quality to download:"
        
        # Create inline keyboard with quality options
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        # Check which thumbnails are available
        available_qualities = {}
        
        for quality, url in thumbnails.items():
            response = requests.head(url)
            if response.status_code == 200:
                # Get file size
                size = response.headers.get('content-length', 0)
                if size and int(size) > 1000:  # Ensure it's a valid image
                    available_qualities[quality] = url
                    file_size = f"({int(int(size)/1024)} KB)" if size else ""
                    buttons.append(types.InlineKeyboardButton(
                        text=f"{quality.upper()} {file_size}", 
                        callback_data=f"thumb_{quality}_{video_id}"
                    ))
        
        if not available_qualities:
            bot.send_message(chat_id, "❌ <b>No thumbnails found</b>\n\nCould not extract thumbnails from this video.")
            return
        
        # Add buttons in rows of 2
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.add(buttons[i], buttons[i+1])
            else:
                keyboard.add(buttons[i])
        
        # Send message with thumbnail options
        bot.send_message(chat_id, caption, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "🔍 <b>Please send a YouTube URL</b>\n\nI can only process YouTube video links. Example:\n\n<code>https://www.youtube.com/watch?v=dQw4w9WgXcQ</code>")

@bot.callback_query_handler(func=lambda call: call.data.startswith('thumb_'))
def handle_thumbnail_selection(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data.split('_')
    
    if len(data) >= 3:
        quality = data[1]
        video_id = data[2]
        
        # Generate thumbnail URL
        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/{quality}default.jpg'
        
        # Download and send the thumbnail
        try:
            bot.send_chat_action(chat_id, 'upload_photo')
            
            # Download the image
            response = requests.get(thumbnail_url, stream=True)
            if response.status_code == 200:
                # Send the image
                bot.send_photo(
                    chat_id, 
                    response.content,
                    caption=f"📸 <b>YouTube Thumbnail</b>\n\nQuality: <code>{quality.upper()}</code>\nVideo ID: <code>{video_id}</code>"
                )
                
                # Answer the callback query
                bot.answer_callback_query(call.id, "✅ Thumbnail sent!")
            else:
                bot.answer_callback_query(call.id, "❌ Failed to download thumbnail")
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Error: {str(e)}")

# ==== MAIN ====
if __name__ == "__main__":
    # Start Flask app for production
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
