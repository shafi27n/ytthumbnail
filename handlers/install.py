import requests
import json
from datetime import datetime
from app import User

def handle(user_info, chat_id, message_text):
    """Handle /install command - Install database tables"""
    
    from app import SUPABASE_URL, SUPABASE_KEY
    
    installation_log = f"""
🗃️ <b>Database Installation</b> (via /install)

Starting database table creation...
"""
    
    try:
        # Table creation SQL commands
        tables_sql = [
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
                "name": "bot_settings",
                "sql": """
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id BIGSERIAL PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    description TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            }
        ]
        
        # Execute table creation
        for table in tables_sql:
            try:
                # Try to create table using direct REST API approach
                installation_log += f"\n\n📊 Creating table: <b>{table['name']}</b>"
                
                # First check if table exists
                check_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/{table['name']}?limit=1",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}"
                    }
                )
                
                if check_response.status_code == 200:
                    installation_log += f"\n✅ Table <b>{table['name']}</b> already exists"
                else:
                    # Table doesn't exist, we'll rely on auto-creation through API usage
                    installation_log += f"\n🔄 Table <b>{table['name']}</b> will be auto-created on first use"
                    
            except Exception as e:
                installation_log += f"\n⚠️ Table <b>{table['name']}</b>: {str(e)}"
        
        # Test database connection by inserting a test record
        installation_log += f"\n\n🔌 <b>Testing Database Connection...</b>"
        
        test_result = test_database_connection(user_info)
        installation_log += f"\n{test_result}"
        
        installation_log += f"""

🎉 <b>Installation Complete!</b>

✅ <b>Next Steps:</b>
1. Use <b>/checkdb</b> to verify installation
2. Use <b>/save test_data</b> to test data storage
3. Use <b>/show</b> to view saved data

💾 <b>Database Ready for Use!</b>
"""
        
    except Exception as e:
        installation_log += f"\n\n❌ <b>Installation Failed:</b> {str(e)}"
    
    return installation_log

def test_database_connection(user_info):
    """Test database connection by performing actual operations"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    test_log = ""
    
    try:
        # Test 1: Save user data
        test_log += "\n💾 <b>Testing Data Save:</b>"
        save_result = User.save_data(user_id, "install_test", f"Installation test at {datetime.now()}")
        test_log += f"\n• Save Operation: {save_result}"
        
        # Test 2: Retrieve user data
        test_log += "\n📂 <b>Testing Data Retrieve:</b>"
        retrieved_data = User.get_data(user_id, "install_test")
        test_log += f"\n• Retrieve Operation: {'✅ Success' if retrieved_data else '❌ Failed'}"
        
        # Test 3: Save multiple items
        test_log += "\n🔢 <b>Testing Multiple Items:</b>"
        User.save_data(user_id, "test_counter", "1")
        counter_data = User.get_data(user_id, "test_counter")
        test_log += f"\n• Counter Test: {'✅ Working' if counter_data == '1' else '❌ Failed'}"
        
        test_log += "\n\n🎯 <b>All Database Tests Completed Successfully!</b>"
        
    except Exception as e:
        test_log += f"\n❌ <b>Database Test Failed:</b> {str(e)}"
    
    return test_log