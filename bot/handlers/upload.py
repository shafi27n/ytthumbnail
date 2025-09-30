import requests
import os
from datetime import datetime

def handle_upload(user_info, chat_id, message_text):
    """Handle /upload command with HTML formatting"""
    
    first_name = user_info.get('first_name', 'Friend')
    username = user_info.get('username', '')
    user_id = user_info.get('id', 'Unknown')
    
    instruction_text = f"""
📤 <b>Universal Upload System</b>

👋 <b>Hello {first_name}!</b>

🔄 <b>What you can upload:</b>
• 📸 <b>Photos</b> - Send as photo
• 📄 <b>Documents</b> - Any file type  
• 🎥 <b>Videos</b> - Video files
• 🎵 <b>Audio</b> - Music/audio files
• 🎤 <b>Voice messages</b> - Voice recordings

⚡ <b>How it works:</b>
1. Send any file/media to this chat
2. I'll automatically forward it to @refffrrr
3. You'll get a direct download link
4. Share the link with anyone

🔧 <b>Upload Steps:</b>
1. <code>/upload</code> - See these instructions
2. <b>Select file</b> from your device
3. <b>Send as file</b> (not as photo for documents)
4. <b>Wait for processing</b>
5. <b>Get shareable link</b>

👤 <b>Your Info:</b>
• <b>Name:</b> {first_name}
• <b>User ID:</b> <code>{user_id}</code>
• <b>Chat ID:</b> <code>{chat_id}</code>
{f'• <b>Username:</b> @{username}' if username else '• <b>Username:</b> Not set'}

📦 <b>File Requirements:</b>
• <b>Max size:</b> 20MB (Telegram limit)
• <b>Supported types:</b> All common formats
• <b>Processing:</b> Instant forwarding

🚀 <b>Ready to upload? Just send your file now!</b>

💡 <b>Pro Tip:</b> For photos, send as <b>photo</b> for better quality.
For documents, send as <b>file</b> to preserve original format.
    """
    
    return instruction_text

def handle_photo(message):
    """Handle photo uploads automatically"""
    return process_media_upload(message, 'photo', '📸', 'Photo')

def handle_document(message):
    """Handle document uploads automatically"""
    return process_media_upload(message, 'document', '📄', 'Document')

def handle_video(message):
    """Handle video uploads automatically"""
    return process_media_upload(message, 'video', '🎥', 'Video')

def handle_audio(message):
    """Handle audio uploads automatically"""
    return process_media_upload(message, 'audio', '🎵', 'Audio')

def handle_voice(message):
    """Handle voice message uploads automatically"""
    return process_media_upload(message, 'voice', '🎤', 'Voice Message')

def process_media_upload(message, media_type, emoji, media_name):
    """Process media upload and forward to channel"""
    try:
        chat_id = message.get('chat', {}).get('id')
        user_info = message.get('from', {})
        message_id = message.get('message_id')
        
        first_name = user_info.get('first_name', 'User')
        username = user_info.get('username', '')
        user_id = user_info.get('id', 'Unknown')
        
        # Get file information
        file_id = get_file_id_from_message(message, media_type)
        file_url = get_telegram_file_url(file_id) if file_id else None
        
        # Forward to channel @refffrrr
        forward_result = forward_to_channel(chat_id, message_id)
        
        # Get file details
        file_size = get_file_size(message, media_type)
        mime_type = get_mime_type(message, media_type)
        
        if forward_result.get('ok'):
            # Success response
            channel_message_id = forward_result['result']['message_id']
            
            success_text = f"""
{emoji} <b>{media_name} Successfully Uploaded!</b>

✅ <b>Status:</b> Forwarded to @refffrrr
👤 <b>Uploaded by:</b> {first_name} {f'(@{username})' if username else ''}
📁 <b>File Type:</b> {media_name}
{f'📊 <b>File Size:</b> {file_size}' if file_size else ''}
{f'🎯 <b>File Format:</b> {mime_type}' if mime_type else ''}

🔗 <b>Direct Download Link:</b>
<code>{file_url}</code>

🆔 <b>File Information:</b>
• <b>File ID:</b> <code>{file_id}</code>
• <b>Channel Message ID:</b> <code>{channel_message_id}</code>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Upload Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <b>How to share:</b>
Copy the download link above and share it with anyone.
The link will work as long as the file exists on Telegram servers.

📤 <b>Want to upload more?</b> Just send another file!

🔗 <b>Quick Share:</b> <code>{file_url}</code>
            """
            
            return {
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': success_text,
                'parse_mode': 'HTML'
            }
        else:
            # Forward failed
            error_text = f"""
❌ <b>Upload Failed!</b>

⚠️ <b>Error:</b> Could not forward to @refffrrr
🔧 <b>Reason:</b> {forward_result.get('description', 'Unknown error')}

👤 <b>User:</b> {first_name}
📁 <b>File Type:</b> {media_name}
{f'🔗 <b>File URL:</b> <code>{file_url}</code>' if file_url else ''}

🔄 <b>Troubleshooting:</b>
1. Check if @refffrrr channel exists
2. Verify bot has posting permission in channel
3. Try with a different file
4. Check file size (max 20MB)

📞 <b>Need assistance?</b> Contact the administrator.

🚀 <b>Try again:</b> Send the file one more time.
            """
            
            return {
                'method': 'sendMessage', 
                'chat_id': chat_id,
                'text': error_text,
                'parse_mode': 'HTML'
            }
            
    except Exception as e:
        error_response = {
            'method': 'sendMessage',
            'chat_id': message.get('chat', {}).get('id'),
            'text': f'❌ <b>System Error:</b>\n<code>{str(e)}</code>\n\nPlease try again later.',
            'parse_mode': 'HTML'
        }
        return error_response

def forward_to_channel(chat_id, message_id, target_channel='@refffrrr'):
    """Forward message to channel with error handling"""
    try:
        bot_token = os.environ.get('BOT_TOKEN')
        if not bot_token:
            return {'ok': False, 'description': 'Bot token not configured'}
        
        forward_data = {
            'chat_id': target_channel,
            'from_chat_id': chat_id,
            'message_id': message_id
        }
        
        forward_url = f"https://api.telegram.org/bot{bot_token}/forwardMessage"
        response = requests.post(forward_url, json=forward_data, timeout=10)
        return response.json()
        
    except requests.exceptions.Timeout:
        return {'ok': False, 'description': 'Request timeout - try again'}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'description': 'Connection error - check internet'}
    except Exception as e:
        return {'ok': False, 'description': f'Forwarding error: {str(e)}'}

def get_telegram_file_url(file_id):
    """Get direct URL for Telegram file"""
    try:
        bot_token = os.environ.get('BOT_TOKEN')
        if not bot_token:
            return None
            
        file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        response = requests.get(file_info_url, timeout=10)
        file_info = response.json()
        
        if file_info.get('ok'):
            file_path = file_info['result']['file_path']
            return f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        return None
    except Exception as e:
        print(f"Error getting file URL: {e}")
        return None

def get_file_id_from_message(message, media_type):
    """Extract file ID from different media types"""
    try:
        if media_type == 'photo':
            # Get the highest quality photo (last in array)
            photos = message.get('photo', [])
            return photos[-1].get('file_id') if photos else None
        elif media_type in ['document', 'video', 'audio', 'voice']:
            media_obj = message.get(media_type, {})
            return media_obj.get('file_id')
        return None
    except Exception as e:
        print(f"Error getting file ID: {e}")
        return None

def get_file_size(message, media_type):
    """Get file size in readable format"""
    try:
        if media_type == 'photo':
            photos = message.get('photo', [])
            if photos:
                file_size = photos[-1].get('file_size', 0)
        elif media_type in ['document', 'video', 'audio', 'voice']:
            media_obj = message.get(media_type, {})
            file_size = media_obj.get('file_size', 0)
        else:
            return None
            
        if file_size:
            if file_size < 1024:
                return f"{file_size} B"
            elif file_size < 1024 * 1024:
                return f"{file_size / 1024:.1f} KB"
            else:
                return f"{file_size / (1024 * 1024):.1f} MB"
        return None
    except Exception:
        return None

def get_mime_type(message, media_type):
    """Get MIME type of the file"""
    try:
        if media_type in ['document', 'audio']:
            media_obj = message.get(media_type, {})
            return media_obj.get('mime_type', 'Unknown')
        elif media_type == 'video':
            return 'video/mp4'
        elif media_type == 'photo':
            return 'image/jpeg'
        elif media_type == 'voice':
            return 'audio/ogg'
        return 'Unknown'
    except Exception:
        return 'Unknown'
