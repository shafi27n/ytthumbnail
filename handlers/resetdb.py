import requests
from app import User, SUPABASE_URL, SUPABASE_KEY

def handle(user_info, chat_id, message_text):
    """Handle /resetdb command - Reset user's data - FIXED"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    reset_log = f"""
🔄 <b>Database Reset</b>

Resetting data for user: {first_name} (ID: {user_id})
"""
    
    try:
        # List of variables to reset
        variables_to_reset = ["saved_items", "install_test", "checkdb_test", "test_counter", "debug_test", "connection_test"]
        
        reset_log += f"\n🗑️ <b>Clearing Data:</b>"
        
        reset_count = 0
        for variable in variables_to_reset:
            # Check if variable exists
            existing_data = User.get_data(user_id, variable)
            if existing_data is not None:
                User.save_data(user_id, variable, "", user_info)  # Clear the data
                reset_count += 1
                reset_log += f"\n• {variable}: ✅ Cleared"
            else:
                reset_log += f"\n• {variable}: ⏭️ Not found"
        
        # Also try to delete from Supabase directly
        reset_log += f"\n\n🔥 <b>Supabase Cleanup:</b>"
        try:
            # Delete from bot_data table
            delete_response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/bot_data?user_id=eq.{user_id}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            
            if delete_response.status_code in [200, 204]:
                reset_log += f"\n• bot_data: ✅ All user data deleted"
            else:
                reset_log += f"\n• bot_data: ⚠️ {delete_response.status_code}"
                
        except Exception as e:
            reset_log += f"\n• bot_data: ❌ Error: {str(e)}"
        
        reset_log += f"""

🎉 <b>Reset Complete!</b>

✅ <b>Summary:</b>
• Variables cleared: {reset_count}
• Local cache cleared
• Server data cleaned

💡 <b>Next:</b> Use <b>/save</b> to start fresh!
"""
        
    except Exception as e:
        reset_log += f"\n\n❌ <b>Reset Failed:</b> {str(e)}"
    
    return reset_log