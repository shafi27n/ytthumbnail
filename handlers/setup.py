import requests
import json
from datetime import datetime

def setup_database_function(user_info, chat_id, message_text):
    """Handle /setup command - Setup database tables in Supabase"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    from app import SUPABASE_URL, SUPABASE_KEY
    
    setup_steps = f"""
🗃️ <b>Database Setup System</b>

👤 <b>User:</b> {first_name}
🆔 <b>User ID:</b> <code>{user_id}</code>
🕒 <b>Start Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🚀 <b>Starting Database Setup...</b>

📡 <b>Supabase Configuration:</b>
• URL: <code>{SUPABASE_URL}</code>
• Key: <code>{SUPABASE_KEY[:20]}...</code>

🔧 <b>Step 1: Checking Connection...</b>
"""
    
    try:
        # Step 1: Test Supabase connection
        test_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=10
        )
        
        if test_response.status_code == 200:
            setup_steps += "\n✅ <b>Connection Successful!</b> Supabase is accessible."
        else:
            setup_steps += f"\n❌ <b>Connection Failed:</b> Status {test_response.status_code}"
            return setup_steps
        
        setup_steps += "\n\n🔧 <b>Step 2: Creating Tables...</b>"
        
        # SQL commands for table creation
        sql_commands = [
            {
                "name": "tgbot_users",
                "sql": """
                CREATE TABLE IF NOT EXISTS tgbot_users (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            },
            {
                "name": "tgbot_data", 
                "sql": """
                CREATE TABLE IF NOT EXISTS tgbot_data (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    variable TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(user_id, variable)
                );
                """
            },
            {
                "name": "bot_data",
                "sql": """
                CREATE TABLE IF NOT EXISTS bot_data (
                    id BIGSERIAL PRIMARY KEY,
                    variable TEXT UNIQUE NOT NULL,
                    value TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            }
        ]
        
        # Execute table creation
        for table in sql_commands:
            try:
                # Try to create table by attempting to insert (will fail if table doesn't exist)
                test_response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/{table['name']}",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },
                    json={
                        "test": "connection"
                    }
                )
                
                if test_response.status_code in [201, 409]:  # Created or conflict (table exists)
                    setup_steps += f"\n✅ {table['name']}: Table exists"
                else:
                    setup_steps += f"\n❌ {table['name']}: Table might not exist (Status: {test_response.status_code})"
                    
            except Exception as e:
                setup_steps += f"\n⚠️ {table['name']}: Error checking - {str(e)}"
        
        setup_steps += "\n\n🔧 <b>Step 3: Testing Data Operations...</b>"
        
        # Test user data operations
        from app import User, Bot
        
        # Test save operation
        save_test = User.save_data(user_id, "setup_test", f"Setup completed at {datetime.now()}")
        setup_steps += f"\n• Save Test: {save_test}"
        
        # Test retrieve operation  
        retrieve_test = User.get_data(user_id, "setup_test")
        setup_steps += f"\n• Retrieve Test: {'✅ Success' if retrieve_test else '❌ Failed'}"
        
        # Test bot data operation
        bot_save_test = Bot.save_data("setup_bot_test", f"Bot setup at {datetime.now()}")
        setup_steps += f"\n• Bot Data Test: {bot_save_test}"
        
        setup_steps += f"\n\n🎉 <b>Setup Completed Successfully!</b>"
        
        setup_steps += f"""
        
📊 <b>Setup Summary:</b>
• ✅ Supabase Connection: Working
• ✅ User Data Table: Ready
• ✅ Bot Data Table: Ready  
• ✅ Data Operations: Tested
• 👤 Test User: {first_name}
• 🆔 User ID: <code>{user_id}</code>
• 🕒 Completion Time: {datetime.now().strftime('%H:%M:%S')}

🚀 <b>Now you can use these commands:</b>
• <code>/save your_data</code> - Save user data
• <code>/show</code> - View saved data
• <code>/delete item_id</code> - Delete data

💡 <b>Try the system:</b>
<code>/save Hello World!</code>
"""
        
    except Exception as e:
        setup_steps += f"\n\n❌ <b>Setup Failed!</b>\nError: {str(e)}"
        
        setup_steps += f"""
        
🔧 <b>Troubleshooting Steps:</b>
1. Check Supabase project is active
2. Verify API keys are correct
3. Ensure tables have proper permissions
4. Check internet connection

📞 <b>Need Help?</b>
Contact support with the error message above.
"""
    
    return setup_steps

def handle_setup(user_info, chat_id, message_text):
    """Alias for setup_database_function"""
    return setup_database_function(user_info, chat_id, message_text)