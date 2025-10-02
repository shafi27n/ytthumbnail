import requests
from datetime import datetime

def handle(user_info, chat_id, message_text):
    """Handle /checkdb command - Check database status and tables"""
    
    from app import SUPABASE_URL, SUPABASE_KEY, User
    
    check_log = f"""
🔍 <b>Database Status Check</b>

Checking Supabase database tables and connectivity...
"""
    
    try:
        # List of tables to check
        tables_to_check = ["tgbot_users", "tgbot_data", "bot_settings"]
        
        check_log += f"\n📊 <b>Table Status:</b>"
        
        for table_name in tables_to_check:
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
                        f"{SUPABASE_URL}/rest/v1/{table_name}?select=id",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}"
                        }
                    )
                    
                    row_count = len(count_response.json()) if count_response.status_code == 200 else "N/A"
                    check_log += f"\n✅ <b>{table_name}</b>: EXISTS ({row_count} rows)"
                else:
                    check_log += f"\n❌ <b>{table_name}</b>: MISSING (Error: {response.status_code})"
                    
            except Exception as e:
                check_log += f"\n⚠️ <b>{table_name}</b>: ERROR - {str(e)}"
        
        # Test current user's data operations
        user_id = user_info.get('id')
        check_log += f"\n\n👤 <b>User Data Test (ID: {user_id}):</b>"
        
        # Test save operation
        test_timestamp = datetime.now().isoformat()
        save_result = User.save_data(user_id, "checkdb_test", test_timestamp)
        check_log += f"\n• Save Test: {save_result}"
        
        # Test retrieve operation
        retrieved_data = User.get_data(user_id, "checkdb_test")
        if retrieved_data == test_timestamp:
            check_log += f"\n• Retrieve Test: ✅ Data Integrity Verified"
        else:
            check_log += f"\n• Retrieve Test: ❌ Data Mismatch"
        
        # Check user's total data records
        try:
            user_data_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/tgbot_data?user_id=eq.{user_id}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            
            if user_data_response.status_code == 200:
                user_records = len(user_data_response.json())
                check_log += f"\n• Your Data Records: {user_records}"
            else:
                check_log += f"\n• Your Data Records: Unable to fetch"
                
        except Exception as e:
            check_log += f"\n• Your Data Records: Error - {str(e)}"
        
        # Overall status
        check_log += f"\n\n🎯 <b>Overall Database Status: ✅ OPERATIONAL</b>"
        check_log += f"\n🕒 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
    except Exception as e:
        check