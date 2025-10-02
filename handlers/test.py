def handle(user_info, chat_id, message_text):
    """Handle /test command - check bot status"""
    
    from app import TELETHON_AVAILABLE, API_ID, API_HASH
    
    if TELETHON_AVAILABLE:
        telegram_status = "✅ Enabled"
        api_info = f"""
🔧 <b>API Configuration:</b>
• API_ID: <code>{API_ID}</code>
• API_HASH: <code>{API_HASH[:10]}...</code>
"""
    else:
        telegram_status = "❌ Disabled"
        api_info = """
⚠️ <b>Setup Required:</b>
Visit https://my.telegram.org to get API credentials
"""
    
    return f"""
🧪 <b>Bot Status Test</b>

🤖 <b>Bot Status:</b> ✅ Running
🔐 <b>Telegram Features:</b> {telegram_status}

{api_info}

💡 <b>Next Steps:</b>
• If disabled, configure API credentials
• If enabled, try <code>/login</code>
"""