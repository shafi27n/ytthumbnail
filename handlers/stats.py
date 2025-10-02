import requests
from datetime import datetime

def handle(user_info, chat_id, message_text):
    """Handle /stats command - Show database statistics"""
    
    from app import SUPABASE_URL, SUPABASE_KEY, command_handlers
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    stats_log = f"""
📈 <b>Bot Statistics</b>

🕒 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 User: {first_name} (ID: {user_id})
"""
    
    try:
        # Database Statistics
        stats_log += f"\n🗃️ <b>Database Statistics:</b>"
        
        # Total users count
        try:
            users_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/tgbot_users?select=id",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            total_users = len(users_response.json()) if users_response.status_code == 200 else "N/A"
            stats_log += f"\n• Total Users: {total_users}"
        except:
            stats_log += f"\n• Total Users: N/A"
        
        # Total data records
        try:
            data_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/tgbot_data?select=id",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            total_records = len(data_response.json()) if data_response.status_code == 200 else "N/A"
            stats_log += f"\n• Total Data Records: {total_records}"
        except:
            stats_log += f"\n• Total Data Records: N/A"
        
        # Current user's stats
        stats_log += f"\n\n👤 <b>Your Statistics:</b>"
        
        from app import User
        
        # Count user's variables
        user_variables = 0
        test_vars = ["saved_items", "install_test", "checkdb_test", "test_counter", "debug_test"]
        
        for var in test_vars:
            if User.get_data(user_id, var) is not None:
                user_variables += 1
        
        stats_log += f"\n• Your Active Variables: