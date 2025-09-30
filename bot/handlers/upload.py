import requests
import os
from flask import jsonify

def handle_upload(user_info, chat_id, message_text):
    """Handle /upload command with HTML formatting"""
    
    first_name = user_info.get('first_name', 'Friend')
    username = user_info.get('username', '')
    
    instruction_text = f"""
📤 <b>Image Upload System</b>

👋 <b>Hello {first_name}!</b>

📷 <b>How to upload:</b>
1. <b>Take a photo</b> or <b>select from gallery</b>
2. <b>Send it here</b> as a photo (not as file)
3. I'll <b>forward to @refffrrr</b>
4. You'll get the <b>image link</b>

⚡ <b>Features:</b>
• Auto-forward to @refffrrr
• Get direct image link
• Fast processing
• Secure handling

👤 <b>Your Info:</b>
• <b>Name:</b> {first_name}
{f'• <b>Username:</b> @{username}' if username else ''}
• <b>User ID:</b> <code>{user_info.get('id', 'Unknown')}</code>

⚠️ <b>Note:</b>
• Send only <b>images</b> (photos)
• Max size: <b>10MB</b>
• Supported formats: <b>JPG, PNG, JPEG</b>

🚀 <b>Ready to upload? Just send your photo!</b>
    """
    
    return instruction_text

def handle_photo_upload(update):
    """Handle actual photo upload and forward to @refffrrr"""
    try:
        # Extract photo information
        message = update.get('message', {})
        user_info = message.get('from', {})
        chat_id = message.get('chat', {}).get('id')
        photo = message.get('photo', [{}])[-1]  # Get highest quality photo
        file_id = photo.get('file_id')
        
        if not file_id:
            return jsonify({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': '❌ <b>Error:</b> No photo found in message',
                'parse_mode': 'HTML'
            })
        
        # Get file info from Telegram
        bot_token = os.environ.get('BOT_TOKEN')
        file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        file_info_response = requests.get(file_info_url).json()
        
        if not file_info_response.get('ok'):
            return jsonify({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': '❌ <b>Error:</b> Could not get file information',
                'parse_mode': 'HTML'
            })
        
        file_path = file_info_response['result']['file_path']
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        
        # Forward photo to @refffrrr
        forward_data = {
            'chat_id': '@refffrrr',  # Channel username
            'from_chat_id': chat_id,
            'message_id': message.get('message_id')
        }
        
        forward_url = f"https://api.telegram.org/bot{bot_token}/forwardMessage"
        forward_response = requests.post(forward_url, json=forward_data).json()
        
        first_name = user_info.get('first_name', 'User')
        username = user_info.get('username', '')
        
        if forward_response.get('ok'):
            # Success response
            success_text = f"""
✅ <b>Image Successfully Uploaded!</b>

👤 <b>Uploaded by:</b> {first_name} {f'(@{username})' if username else ''}
📁 <b>File ID:</b> <code>{file_id}</code>
🔗 <b>Direct Link:</b> <code>{file_url}</code>

📤 <b>Status:</b> Forwarded to @refffrrr
🎯 <b>Message ID:</b> <code>{forward_response['result']['message_id']}</code>

💡 <b>You can share this link:</b>
<code>{file_url}</code>

📸 <b>Want to upload more?</b> Just send another photo!
            """
            
            return jsonify({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': success_text,
                'parse_mode': 'HTML'
            })
        else:
            # Forward failed
            error_text = f"""
❌ <b>Upload Failed!</b>

⚠️ <b>Error:</b> Could not forward to @refffrrr
🔧 <b>Reason:</b> {forward_response.get('description', 'Unknown error')}

📞 <b>Please try again:</b>
1. Check if @refffrrr exists
2. Make sure bot has permission
3. Try with a different photo

🔄 <b>Need help?</b> Contact administrator.
            """
            
            return jsonify({
                'method': 'sendMessage', 
                'chat_id': chat_id,
                'text': error_text,
                'parse_mode': 'HTML'
            })
            
    except Exception as e:
        error_response = {
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': f'❌ <b>System Error:</b> <code>{str(e)}</code>',
            'parse_mode': 'HTML'
        }
        return jsonify(error_response)
