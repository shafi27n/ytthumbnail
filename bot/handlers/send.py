import html
from telegram import Update
from telegram.ext import ContextTypes

async def handle_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /send command to actually forward content to @refffrrr"""
    
    user = update.effective_user
    message = update.effective_message
    chat_id = update.effective_chat.id
    
    # Check if message is a reply
    if message.reply_to_message:
        try:
            # Forward the replied message to @refffrrr
            await message.reply_to_message.forward(chat_id="@refffrrr")
            
            # Send confirmation to user
            response_text = f"""
✅ <b>কন্টেন্ট সফলভাবে ফরওয়ার্ড করা হয়েছে!</b>

📤 <b>টার্গেট:</b> @refffrrr
👤 <b>সেন্ডার:</b> {user.first_name}
🆔 <b>ইউজার আইডি:</b> <code>{user.id}</code>

🎯 <b>স্ট্যাটাস:</b> আপনার কন্টেন্ট সফলভাবে পাঠানো হয়েছে।
            """
            await message.reply_text(response_text, parse_mode='HTML')
            
        except Exception as e:
            error_text = f"""
❌ <b>ফরওয়ার্ড করতে সমস্যা হয়েছে!</b>

⚠️ <b>ত্রুটি:</b> {str(e)}

🔧 <b>সমাধান:</b>
• ইন্টারনেট কানেকশন চেক করুন
• বটটি @refffrrr গ্রুপে আছে কিনা নিশ্চিত করুন
• আবার চেষ্টা করুন
            """
            await message.reply_text(error_text, parse_mode='HTML')
    
    # Check if there's text after command
    elif context.args:
        text_to_send = ' '.join(context.args)
        try:
            # Send text directly to @refffrrr
            await context.bot.send_message(
                chat_id="@refffrrr",
                text=f"""
📨 <b>নতুন মেসেজ</b>

💬 <b>কন্টেন্ট:</b>
{html.escape(text_to_send)}

👤 <b>সেন্ডার:</b> {user.first_name}
🆔 <b>ইউজার আইডি:</b> <code>{user.id}</code>
                """,
                parse_mode='HTML'
            )
            
            # Send confirmation
            response_text = f"""
✅ <b>টেক্সট মেসেজ সফলভাবে পাঠানো হয়েছে!</b>

📤 <b>টার্গেট:</b> @refffrrr
👤 <b>সেন্ডার:</b> {user.first_name}

📝 <b>মেসেজ:</b>
<i>{html.escape(text_to_send)}</i>
            """
            await message.reply_text(response_text, parse_mode='HTML')
            
        except Exception as e:
            error_text = f"""
❌ <b>মেসেজ পাঠাতে সমস্যা!</b>

⚠️ <b>ত্রুটি:</b> {str(e)}
            """
            await message.reply_text(error_text, parse_mode='HTML')
    
    else:
        # Show instructions
        response_text = f"""
📤 <b>সেন্ড কমান্ড</b>

👋 হ্যালো <b>{user.first_name}</b>!

🚀 <b>ব্যবহার পদ্ধতি:</b>

1. <b>রিপ্লাই মেথড:</b>
   • যেকোনো মেসেজ/ছবি/ভিডিও রিপ্লাই করুন
   • রিপ্লাই করে লিখুন: <code>/send</code>

2. <b>টেক্সট মেথড:</b>
   • সরাসরি লিখুন: <code>/send আপনার_মেসেজ</code>

📁 <b>সাপোর্টেড কন্টেন্ট:</b>
✅ টেক্সট মেসেজ
✅ ছবি (JPEG, PNG, GIF) 
✅ ভিডিও (MP4, MOV)
✅ ডকুমেন্ট (PDF, DOC, TXT)
✅ অডিও (MP3, VOICE)
✅ স্টিকার

🎯 <b>টার্গেট:</b> @refffrrr

💡 <b>উদাহরণ:</b>
<code>/send হ্যালো, এটি টেস্ট মেসেজ</code>
        """
        await message.reply_text(response_text, parse_mode='HTML')
