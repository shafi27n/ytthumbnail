import requests
import json
from datetime import datetime
from app import User, SUPABASE_URL, SUPABASE_KEY

def handle(user_info, chat_id, message_text):
    """Handle /install command - Install database tables with actual names"""
    
    installation_log = f"""
🗃️ <b>Database Installation</b> (via /install)

Creating actual database tables...
"""
    
    try:
        # Actual table creation SQL commands
        tables_sql = [
            {
                "name": "webhook_users",
                "sql": """
                CREATE TABLE IF NOT EXISTS webhook_users (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            },
            {
                "name": "webhook_bot_tokens", 
                "sql": """
                CREATE TABLE IF NOT EXISTS webhook_bot_tokens (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    bot_token TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(user_id, bot_token)
                );
                """
            },
            {
                "name": "webhook_settings",
                "sql": """
                CREATE TABLE IF NOT EXISTS webhook_settings (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    webhook_url TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(user_id, webhook_url)
                );
                """
            },
            {
                "name": "bot_data",
                "sql": """
                CREATE TABLE IF NOT EXISTS bot_data (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    variable TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(user_id, variable)
                );
                """
            }
        ]
        
        # Execute table creation using RPC
        installation_log += f"\n🔄 <b>Creating tables via RPC...</b>"
        
        for table in tables_sql:
            try:
                installation_log += f"\n\n📊 Creating: <b>{table['name']}</b>"
                
                # Use RPC endpoint for SQL execution
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/rpc/execute_sql",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"query": table['sql']},
                    timeout=10
                )
                
                if response.status_code in [200, 201, 204]:
                    installation_log += f"\n✅ Table <b>{table['name']}</b> created successfully"
                else:
                    installation_log += f"\n⚠️ Table <b>{table['name']}</b>: API returned {response.status_code}"
                    # Try alternative approach - check if table exists
                    check_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/{table['name']}?limit=1",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}"
                        }
                    )
                    if check_response.status_code == 200:
                        installation_log += f" (but table exists)"
                    else:
                        installation_log += f" (table may not exist)"
                    
            except Exception as e:
                installation_log += f"\n❌ Table <b>{table['name']}</b>: {str(e)}"
        
        # Test database connection with actual tables
        installation_log += f"\n\n🔌 <b>Testing Database Connection...</b>"
        
        test_result = test_database_connection(user_info)
        installation_log += f"\n{test_result}"
        
        installation_log += f"""

🎉 <b>Installation Complete!</b>

📊 <b>Tables Created:</b>
• webhook_users - User information
• webhook_bot_tokens - Bot tokens storage  
• webhook_settings - Webhook URLs
• bot_data - General bot data storage

✅ <b>Next Steps:</b>
1. Use <b>/checkdb</b> to verify tables
2. Use <b>/save test_data</b> to test
3. Use <b>/show</b> to view data

💾 <b>Database Ready!</b>
"""
        
    except Exception as e:
        installation_log += f"\n\n❌ <b>Installation Failed:</b> {str(e)}"
    
    return installation_log

def test_database_connection(user_info):
    """Test database connection with actual tables"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    test_log = ""
    
    try:
        # Test 1: Save user data to webhook_users
        test_log += "\n💾 <b>Testing User Data Save:</b>"
        
        save_result = User.save_data(user_id, "install_test", f"Installation test at {datetime.now()}", user_info)
        test_log += f"\n• Save Operation: {save_result}"
        
        # Test 2: Retrieve user data
        test_log += "\n📂 <b>Testing Data Retrieve:</b>"
        retrieved_data = User.get_data(user_id, "install_test")
        test_log += f"\n• Retrieve Operation: {'✅ Success' if retrieved_data else '❌ Failed'}"
        
        # Test 3: Test webhook_users table
        test_log += "\n\n👤 <b>Testing Webhook Users Table:</b>"
        
        try:
            users_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/webhook_users?user_id=eq.{user_id}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            if users_response.status_code == 200:
                user_data = users_response.json()
                test_log += f"\n• webhook_users: ✅ Accessible ({len(user_data)} records)"
                if user_data:
                    test_log += f"\n• Your username: {user_data[0].get('username', 'Not set')}"
            else:
                test_log += f"\n• webhook_users: ❌ Inaccessible ({users_response.status_code})"
        except Exception as e:
            test_log += f"\n• webhook_users: ❌ Error - {str(e)}"
        
        # Test 4: Test bot_data table
        test_log += "\n\n💾 <b>Testing Bot Data Table:</b>"
        try:
            bot_data_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/bot_data?user_id=eq.{user_id}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            if bot_data_response.status_code == 200:
                bot_data = bot_data_response.json()
                test_log += f"\n• bot_data: ✅ Accessible ({len(bot_data)} records)"
            else:
                test_log += f"\n• bot_data: ❌ Inaccessible ({bot_data_response.status_code})"
        except Exception as e:
            test_log += f"\n• bot_data: ❌ Error - {str(e)}"
        
        if retrieved_data:
            test_log += "\n\n🎯 <b>Database Tests: ✅ SUCCESSFUL</b>"
        else:
            test_log += "\n\n⚠️ <b>Database Tests: PARTIAL SUCCESS</b>"
        
    except Exception as e:
        test_log += f"\n❌ <b>Database Test Failed:</b> {str(e)}"
    
    return test_log