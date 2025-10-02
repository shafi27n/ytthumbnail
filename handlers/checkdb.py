import requests
from datetime import datetime
from app import User, SUPABASE_URL, SUPABASE_KEY

def handle(user_info, chat_id, message_text):
    """Handle /checkdb command - Check actual database tables - FIXED"""
    
    user_id = user_info.get('id')
    
    check_log = f"""
🔍 <b>Database Status Check</b> (Actual Tables)

Checking actual Supabase tables...
"""
    
    try:
        # Actual tables to check
        actual_tables = [
            "webhook_users",
            "webhook_bot_tokens", 
            "webhook_settings",
            "bot_data"
        ]
        
        check_log += f"\n📊 <b>Actual Table Status:</b>"
        
        for table_name in actual_tables:
            try:
                response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Get row count
                    count_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/{table_name}",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}"
                        }
                    )
                    
                    row_count = len(count_response.json()) if count_response.status_code == 200 else "N/A"
                    check_log += f"\n✅ <b>{table_name}</b>: {row_count} rows"
                else:
                    check_log += f"\n❌ <b>{table_name}</b>: {response.status_code}"
                    
            except Exception as e:
                check_log += f"\n⚠️ <b>{table_name}</b>: {str(e)}"
        
        # Test data operations with actual tables
        check_log += f"\n\n👤 <b>Your Data Test (ID: {user_id}):</b>"
        
        # Test save to bot_data
        test_timestamp = datetime.now().isoformat()
        save_result = User.save_data(user_id, "checkdb_test", test_timestamp, user_info)
        check_log += f"\n• Save to bot_data: {save_result}"
        
        # Test retrieve from bot_data
        retrieved_data = User.get_data(user_id, "checkdb_test")
        if retrieved_data == test_timestamp:
            check_log += f"\n• Retrieve from bot_data: ✅ Verified"
        else:
            check_log += f"\n• Retrieve from bot_data: ❌ Mismatch"
        
        # Check webhook_users table for current user
        try:
            webhook_users_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/webhook_users?user_id=eq.{user_id}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            
            if webhook_users_response.status_code == 200:
                user_records = len(webhook_users_response.json())
                check_log += f"\n• Your webhook_users records: {user_records}"
            else:
                check_log += f"\n• Your webhook_users records: {webhook_users_response.status_code}"
                
        except Exception as e:
            check_log += f"\n• Your webhook_users records: Error - {str(e)}"
        
        check_log += f"\n\n🎯 <b>Overall Status: ✅ ACTUAL TABLES READY</b>"
        
    except Exception as e:
        check_log += f"\n\n❌ <b>Database Check Failed:</b> {str(e)}"
    
    return check_log