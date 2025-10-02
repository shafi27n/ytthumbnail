import requests
from app import Bot

def handle(user_info, chat_id, message_text):
    """Handle /setup command"""
    
    from app import SUPABASE_URL, SUPABASE_KEY
    
    setup_info = """
🗃️ <b>Database Setup</b>

Setting up Supabase tables...
"""
    
    try:
        # Try to create tables via direct API calls
        tables_created = []
        
        # Check/create tgbot_users
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/tgbot_users",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            if response.status_code == 200:
                tables_created.append("✅ tgbot_users (exists)")
            else:
                tables_created.append("⚠️ tgbot_users (create manually)")
        except:
            tables_created.append("❌ tgbot_users (connection failed)")
        
        # Check/create tgbot_data
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/tgbot_data",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            if response.status_code == 200:
                tables_created.append("✅ tgbot_data (exists)")
            else:
                tables_created.append("⚠️ tgbot_data (create manually)")
        except:
            tables_created.append("❌ tgbot_data (connection failed)")
        
        setup_info += "\n" + "\n".join(tables_created)
        
        setup_info += f"""

📊 <b>Next Steps:</b>
1. Create tables manually in Supabase
2. Run <b>/debug</b> to test connection
3. Use <b>/save</b> to test data storage

🔧 <b>Table SQL:</b>
<b>
CREATE TABLE tgbot_users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tgbot_data (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    variable TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, variable)
);
</b>
"""
        
    except Exception as e:
        setup_info += f"\n❌ <b>Setup Error:</b> {str(e)}"
    
    return setup_info