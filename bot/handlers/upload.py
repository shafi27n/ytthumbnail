import requests
import os
import json
from flask import jsonify

# In-memory storage for upload sessions (production-এ database use করতে হবে)
UPLOAD_SESSIONS = {}

def handle_upload(user_info, chat_id, message_text):
    """Handle /upload command and wait for user reply"""
    
    first_name = user_info.get('first_name', 'Friend')
    user_id = user_info.get('id')
    
    # Create upload session
    UPLOAD_SESSIONS[user_id] = {
        'waiting_for_upload': True,
        'chat_id': chat_id,
        'first_name': first_name
    }
    
    instruction_text = f"""
📤 <b>Upload System Ready!</b>

👋 <b>Hello {first_name}!</b>

🚀 <b>I'm waiting for your file...</b>

🔄 <b>What you can upload:</b>
• 📸 <b>Photos</b> - Send as photo
• 📄 <b>Documents</b> - Any file type  
• 🎥 <b>Videos</b> - Video files
• 🎵 <b>Audio</b> - Music files
• 🎤 <b>Voice messages</b>

⚡ <b>Just send any file now!</b>
I'll automatically forward it to @refffrrr and give you the shareable link.

⏳ <b>Upload session active for 5 minutes</b>

❌ <b>To cancel:</b> Send /cancel or any text message

💡 <b>Supported:</b> All common file types
📦 <b>Max size:</b> 20MB (Telegram limit)
    """
    
    return instruction_text

def handle_photo(message):
    """Handle photo uploads"""
    return process_uploaded_media(message, 'photo', '📸')

def handle_document(message):
    """Handle document uploads""" 
    return process_uploaded_media(message, 'document', '📄')

def handle_video(message):
    """Handle video uploads"""
    return process_uploaded_media(message, 'video', '🎥')

def handle_audio(message):
    """Handle audio uploads"""
    return process_uploaded_media(message, 'audio', '🎵')

def handle_voice(message):
    """Handle voice message uploads"""
    return process_uploaded_media(message, 'voice', '🎤')

def handle_text(message):
    """Handle text messages during upload session"""
    chat_id = message.get('chat', {}).get('id')
    user_info = message.get('from', {})
    user_id = user_info.get('id')
    message_text = message.get('text', '').strip().lower()
    
    # Check if user has active upload session
    if user_id in UPLOAD_SESSIONS:
        # User sent text instead of file - cancel upload session
        del UPLOAD_SESSIONS[user_id]
        
        if message_text in ['/cancel', 'cancel', 'বাতিল']:
            return jsonify(send_telegram_message(
                chat_id,
                "❌ <b>Upload cancelled.</b>\n\n"
                "📤 Want to upload again? Send <code>/upload</code>",
                parse_mode='HTML'
            ))
        else:
            return jsonify(send_telegram_message(
                chat_id,
                "ℹ️ <b>Upload session ended.</b>\n\n"
                "You sent a text message instead of a file.\n\n"
                "📤 To upload files, send <code>/upload</code> again",
                parse_mode='HTML'
            ))
    
    return None

def process_uploaded_media(message, media_type, emoji):
    """Process uploaded media during active session"""
    try:
        chat_id = message.get('chat', {}).get('id')
        user_info = message.get('from', {})
        user_id = user_info.get('id')
        message_id = message.get('message_id')
        
        first_name = user_info.get('first_name', 'User')
        username = user_info.get('username', '')
        
        # Check if user has active upload session
        if user_id not in UPLOAD_SESSIONS:
            return jsonify(send_telegram_message(
                chat_id,
                "❌ <b>No active upload session!</b>\n\n"
                "💡 <b>To upload files:</b>\n"
                "1. Send <code>/upload</code> first\n"
                "2. Then send your file\n\n"
                "🚀 <b>Start now:</b> <code>/upload</code>",
                parse_mode='HTML'
            ))
        
        # Clear the upload session
        del UPLOAD_SESSIONS[user_id]
        
        # Forward to channel
        forward_result = forward_to_channel(chat_id, message_id, '@refffrrr')
        
        if forward_result.get('ok'):
            channel_message_id = forward_result['result']['message_id']
            file_link = f"https://cmt.me/refffrrr/{channel_message_id}"
            
            media_names = {
                'photo': 'Photo',
                'document': 'Document', 
                'video': 'Video',
                'audio': 'Audio',
                'voice': 'Voice Message'
            }
            
            media_name = media_names.get(media_type, 'File')
            
            success_text = f"""
{emoji} <b>{media_name} Successfully Uploaded!</b>

✅ <b>Status:</b> Forwarded to @refffrrr
👤 <b>Uploaded by:</b> {first_name} {f'(@{username})' if username else ''}
📁 <b>File Type:</b> {media_name}
🔗 <b>Shareable Link:</b> 
<code>{file_link}</code>

📤 <b>Share this link with anyone!</b>

🚀 <b>Want to upload more?</b> 
Send <code>/upload</code> again!
            """
            
            return jsonify(send_telegram_message(
                chat_id,
                success_text,
                parse_mode='HTML'
            ))
        else:
            error_text = f"""
❌ <b>Upload Failed!</b>

⚠️ <b>Error:</b> Could not forward to @refffrrr
🔧 <b>Reason:</b> {forward_result.get('description', 'Unknown error')}

🔄 <b>Please try:</b>
1. Make sure @refffrrr channel exists
2. Check if bot has posting permission
3. Try with a different file
4. Use <code>/upload</code> command again

📞 <b>Need help?</b> Contact administrator.
            """
            
            return jsonify(send_telegram_message(
                chat_id, 
                error_text,
                parse_mode='HTML'
            ))
            
    except Exception as e:
        # Clear session on error
        if user_id in UPLOAD_SESSIONS:
            del UPLOAD_SESSIONS[user_id]
            
        return jsonify(send_telegram_message(
            chat_id,
            f'❌ <b>Upload Error:</b> <code>{str(e)}</code>\n\n'
            f'🔄 <b>Please try again with</b> <code>/upload</code>',
            parse_mode='HTML'
        ))

def forward_to_channel(chat_id, message_id, target_channel='@refffrrr'):
    """Forward message to channel"""
    try:
        bot_token = os.environ.get('BOT_TOKEN')
        forward_data = {
            'chat_id': target_channel,
            'from_chat_id': chat_id,
            'message_id': message_id
        }
        
        forward_url = f"https://api.telegram.org/bot{bot_token}/forwardMessage"
        response = requests.post(forward_url, json=forward_data, timeout=10)
        return response.json()
    except Exception as e:
        return {'ok': False, 'description': str(e)}

def send_telegram_message(chat_id, text, parse_mode='HTML'):
    """Send message with HTML parse mode"""
    return {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }

# Clean up old sessions (basic implementation)
def cleanup_sessions():
    """Clean up old upload sessions (production-এ proper cleanup লাগবে)"""
    global UPLOAD_SESSIONS
    # Simple cleanup - in production use proper TTL-based cleanup
    if len(UPLOAD_SESSIONS) > 1000:
        UPLOAD_SESSIONS.clear()
