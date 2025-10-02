from app import telegram_manager, run_async

def handle(user_info, chat_id, message_text):
    """Handle /accounts command - show logged in accounts"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get user accounts using run_async helper
    accounts = run_async(
        telegram_manager.get_user_accounts(user_id)
    )
    
    if not accounts:
        return """
📭 <b>No Accounts Found</b>

You haven't logged in to any Telegram accounts yet!

🔐 <b>To login:</b>
<code>/login</code>

Then follow the steps:
1. Enter phone number
2. Verify code sent to Telegram
3. Enter 2FA password (if enabled)

📱 You'll receive verification code via Telegram
"""
    
    accounts_text = ""
    for i, account in enumerate(accounts, 1):
        status = "✅" if account.get('is_active', True) else "❌"
        accounts_text += f"""
{i}. {status} <b>{account['name']}</b>
   📱 <code>{account['phone']}</code>
   🆔 @{account['username'] or 'N/A'}
   🔗 <code>/use {account['phone']}</code>
   📤 <code>/send {account['phone']} | username | message</code>
   🚪 <code>/logout {account['phone']}</code>
"""
    
    return f"""
📊 <b>Your Telegram Accounts</b>

👤 <b>User:</b> {first_name}
📈 <b>Total Accounts:</b> {len(accounts)}

{accounts_text}

💡 <b>Quick Actions:</b>
• <code>/use phone_number</code> - Switch account
• <code>/send phone | target | message</code> - Send message
• <code>/logout phone</code> - Logout from bot
• <code>/fulllogout phone</code> - Complete logout (all devices)

🔐 <b>Add more accounts:</b> <code>/login</code>
"""