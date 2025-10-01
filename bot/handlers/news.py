import requests
import json
from flask import jsonify
from datetime import datetime

def handle_news(user_info, chat_id, message_text):
    """Handle /news command - show latest news from API"""
    
    try:
        # API URL
        api_url = "https://myairtel-prod.robi.com.bd/card/api/v1/news"
        
        # Fetch data from API
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': "❌ <b>নিউজ লোড করতে সমস্যা!</b>\n\nদয়া পরে আবার চেষ্টা করুন।",
                'parse_mode': 'HTML'
            })
        
        data = response.json()
        
        if data.get('status') != 'success' or 'data' not in data:
            return jsonify({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': "❌ <b>নিউজ ডাটা পাওয়া যায়নি!</b>\n\nAPI থেকে সঠিক রেসপন্স পাওয়া যায়নি।",
                'parse_mode': 'HTML'
            })
        
        items = data['data'].get('items', [])
        
        if not items:
            return jsonify({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': "📰 <b>কোন নিউজ পাওয়া যায়নি!</b>\n\nবর্তমানে কোন নিউজ নেই।",
                'parse_mode': 'HTML'
            })
        
        # Show first 3 news items
        news_text = "📰 <b>সর্বশেষ খবর</b>\n\n"
        
        for i, item in enumerate(items[:3]):
            title = item.get('title', 'No Title')
            published_date = item.get('published_date', 'Unknown Date')
            description = item.get('description', 'No description available.')
            
            # Shorten description if too long
            if len(description) > 200:
                description = description[:200] + "..."
            
            news_text += f"📌 <b>খবর {i+1}: {title}</b>\n"
            news_text += f"🕐 <b>সময়:</b> {published_date}\n"
            news_text += f"📝 <b>বিস্তারিত:</b> {description}\n"
            
            # Add image if available
            if 'image' in item and item['image'].get('large'):
                news_text += f"🖼️ <b>ছবি:</b> <a href='{item['image']['large']}'>View Image</a>\n"
            
            # Add link if available
            if 'link' in item and item['link'].get('url'):
                news_text += f"🔗 <b>লিংক:</b> <a href='{item['link']['url']}'>Read More</a>\n"
            
            news_text += "─" * 30 + "\n\n"
        
        news_text += "ℹ️ <b>সর্বশেষ ৩টি খবর দেখানো হয়েছে</b>"
        
        # Create keyboard for refresh option
        keyboard = {
            'inline_keyboard': [
                [{'text': '🔄 নিউজ রিফ্রেশ করুন', 'callback_data': 'news_refresh'}],
                [{'text': '📱 মেনুতে ফিরুন', 'callback_data': 'menu_refresh'}]
            ]
        }
        
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': news_text,
            'parse_mode': 'HTML',
            'reply_markup': keyboard,
            'disable_web_page_preview': False
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': "❌ <b>নিউজ লোড করতে সময় বেশি লাগছে!</b>\n\nদয়া পরে আবার চেষ্টা করুন।",
            'parse_mode': 'HTML'
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': f"❌ <b>নেটওয়ার্ক সমস্যা!</b>\n\n<code>ত্রুটি: {str(e)}</code>",
            'parse_mode': 'HTML'
        })
        
    except Exception as e:
        return jsonify({
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': f"❌ <b>নিউজ লোড করতে সমস্যা!</b>\n\n<code>ত্রুটি: {str(e)}</code>",
            'parse_mode': 'HTML'
        })

def handle_all_callbacks(callback_data, user_info, chat_id, message_id):
    """Handle news-related callbacks"""
    
    if callback_data == 'news_refresh':
        return refresh_news(chat_id, message_id, user_info)
    
    return None

def refresh_news(chat_id, message_id, user_info):
    """Refresh news by editing the message"""
    
    try:
        # API URL
        api_url = "https://myairtel-prod.robi.com.bd/card/api/v1/news"
        
        # Fetch data from API
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                'method': 'editMessageText',
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "❌ <b>নিউজ লোড করতে সমস্যা!</b>\n\nদয়া পরে আবার চেষ্টা করুন।",
                'parse_mode': 'HTML'
            })
        
        data = response.json()
        
        if data.get('status') != 'success' or 'data' not in data:
            return jsonify({
                'method': 'editMessageText',
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "❌ <b>নিউজ ডাটা পাওয়া যায়নি!</b>\n\nAPI থেকে সঠিক রেসপন্স পাওয়া যায়নি।",
                'parse_mode': 'HTML'
            })
        
        items = data['data'].get('items', [])
        
        if not items:
            return jsonify({
                'method': 'editMessageText',
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "📰 <b>কোন নিউজ পাওয়া যায়নি!</b>\n\nবর্তমানে কোন নিউজ নেই।",
                'parse_mode': 'HTML'
            })
        
        # Show first 3 news items
        news_text = "📰 <b>সর্বশেষ খবর</b> 🔄\n\n"
        
        for i, item in enumerate(items[:3]):
            title = item.get('title', 'No Title')
            published_date = item.get('published_date', 'Unknown Date')
            description = item.get('description', 'No description available.')
            
            # Shorten description if too long
            if len(description) > 200:
                description = description[:200] + "..."
            
            news_text += f"📌 <b>খবর {i+1}: {title}</b>\n"
            news_text += f"🕐 <b>সময়:</b> {published_date}\n"
            news_text += f"📝 <b>বিস্তারিত:</b> {description}\n"
            
            # Add image if available
            if 'image' in item and item['image'].get('large'):
                news_text += f"🖼️ <b>ছবি:</b> <a href='{item['image']['large']}'>View Image</a>\n"
            
            # Add link if available
            if 'link' in item and item['link'].get('url'):
                news_text += f"🔗 <b>লিংক:</b> <a href='{item['link']['url']}'>Read More</a>\n"
            
            news_text += "─" * 30 + "\n\n"
        
        news_text += "ℹ️ <b>সর্বশেষ ৩টি খবর দেখানো হয়েছে</b>\n🔄 <b>আপডেট করা হয়েছে:</b> " + datetime.now().strftime("%H:%M:%S")
        
        # Create keyboard for refresh option
        keyboard = {
            'inline_keyboard': [
                [{'text': '🔄 নিউজ রিফ্রেশ করুন', 'callback_data': 'news_refresh'}],
                [{'text': '📱 মেনুতে ফিরুন', 'callback_data': 'menu_refresh'}]
            ]
        }
        
        return jsonify({
            'method': 'editMessageText',
            'chat_id': chat_id,
            'message_id': message_id,
            'text': news_text,
            'parse_mode': 'HTML',
            'reply_markup': keyboard,
            'disable_web_page_preview': False
        })
        
    except Exception as e:
        return jsonify({
            'method': 'editMessageText',
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"❌ <b>নিউজ রিফ্রেশ করতে সমস্যা!</b>\n\n<code>ত্রুটি: {str(e)}</code>",
            'parse_mode': 'HTML'
        })
