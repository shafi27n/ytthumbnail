from handlers.allfeatures,af import all_features_handler

def handle_mycustom(user_info, chat_id, message_text):
    """Your existing custom command with added features"""
    
    # Your existing code here
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Check if user wants features
    if ' features' in message_text.lower():
        return all_features_handler(user_info, chat_id, message_text, "mycustom")
    
    # Your original functionality
    return f"""
🎯 <b>My Custom Command</b>

Hello {first_name}! This is your custom command.

💡 <b>Try:</b> <code>/mycustom features</code> to see all available features!

Your original functionality continues here...
"""

def handle_mc(user_info, chat_id, message_text):
    """Short alias"""
    return handle_mycustom(user_info, chat_id, message_text)