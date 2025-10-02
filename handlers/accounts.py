import asyncio
from app import telegram_manager

def handle(user_info, chat_id, message_text):
    """Handle /accounts command - show logged in accounts"""
    
    user_id = user_info.get('id')
    
    # Get user accounts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    accounts = loop.run_until_complete(
        telegram_manager.get_user_accounts(user_id)
    )
    loop.close()
    
    if not accounts:
        return """
📭 <b>No Accounts Found</b>

You haven't logged in to any Telegram accounts yet!

🔐 <b>To login:</b>
<code>/login phone_number</code>

💡 <b>Example:</b>
<b>/login 1234567890</b>

📱 You'll receive verification code via Telegram
"""
    
    accounts_text = ""
    for i, account in enumerate(accounts, 1):
        accounts_text += f"""
{i}. 👤 <b>{account['name']}</b>
   📱 <code>{account['phone']}</code>
   🆔 @{account['username'] or 'N/A'}
   🔗 <code>/use {account['phone']}</code>
"""
    
    return f"""
📊 <b>Your Telegram Accounts</b>

👤 <b>User:</b> {user_info.get('first_name')}
📈 <b>Total Accounts:</b> {len(accounts)}

{accounts_text}

💡 <b>Use account:</b> <code>/use phone_number</code>
📤 <b>Send message:</b> <code>/send phone_number | target | message</code>
🚪 <b>Logout:</b> <code>/logout phone_number</code>
"""