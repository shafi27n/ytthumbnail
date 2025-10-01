from datetime import datetime

def handle_logs(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /logs command - Show user's own logs"""
    
    user_id = user_info.get('id')
    first_name = user_info.get('first_name', 'User')
    
    # Get user's recent logs
    user_logs = bot.get_user_logs(user_id, limit=10)
    
    if not user_logs:
        return f"""
📊 <b>Your Activity Logs</b>

👤 <b>User:</b> {first_name}
🆔 <b>ID:</b> <code>{user_id}</code>

📝 <b>Recent Activity:</b> No logs found

💡 <b>Start interacting:</b>
Use any command to generate logs
Then check back here!
        """
    
    # Format logs for display
    log_entries = []
    for log in user_logs[-10:]:  # Last 10 logs
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')
        message_preview = log['user_message'][:30] + "..." if len(log['user_message']) > 30 else log['user_message']
        log_entries.append(f"• [{timestamp}] {message_preview}")
    
    logs_text = "\n".join(log_entries)
    
    # Get user stats
    all_user_logs = bot.get_user_logs(user_id, limit=1000)
    total_messages = len(all_user_logs)
    
    return f"""
📊 <b>Your Activity Logs</b>

👤 <b>User:</b> {first_name}
🆔 <b>ID:</b> <code>{user_id}</code>
📈 <b>Total Messages:</b> {total_messages}

📝 <b>Recent Activity (Last 10):</b>
{logs_text}

💡 <b>Full logs:</b> Visit web interface
🔧 <b>Admin:</b> <code>/adminlogs</code> for system logs
    """

def handle_adminlogs(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /adminlogs command - Show system logs (admin only)"""
    
    # Simple admin check - you can enhance this
    admin_users = [123456789]  # Add your user ID here
    
    if user_info.get('id') not in admin_users:
        return """
🚫 <b>Access Denied</b>

This command is for administrators only.

💡 <b>Available to you:</b>
<code>/logs</code> - View your own activity logs
        """
    
    # Get system statistics
    stats = bot.get_stats()
    recent_logs = bot.get_recent_logs('system', limit=10)
    
    # Format system logs
    log_entries = []
    for log in recent_logs:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')
        log_entries.append(f"• [{timestamp}] {log['message']}")
    
    logs_text = "\n".join(log_entries) if log_entries else "No system logs"
    
    return f"""
🔧 <b>System Admin Logs</b>

📊 <b>Statistics:</b>
• Total Messages: {stats['total_messages']}
• Total Errors: {stats['total_errors']}
• Active Users: {stats['active_users']}
• System Logs: {stats['total_system_logs']}

⚙️ <b>Recent System Logs:</b>
{logs_text}

🌐 <b>Web Interface:</b>
<code>/logs/web</code> - Full logs in browser
📈 <b>Stats:</b> <code>/stats</code> - Detailed statistics
    """

def handle_stats(user_info, chat_id, message_text, bot=None, **kwargs):
    """Handle /stats command - Show bot statistics"""
    
    stats = bot.get_stats()
    
    return f"""
📈 <b>Bot Statistics</b>

🤖 <b>Bot Performance:</b>
• 📨 Total Messages: <b>{stats['total_messages']}</b>
• ❌ Total Errors: <b>{stats['total_errors']}</b>
• 🔧 System Logs: <b>{stats['total_system_logs']}</b>

👥 <b>User Statistics:</b>
• 👤 Active Users: <b>{stats['active_users']}</b>
• 💬 User Sessions: <b>{stats['user_sessions']}</b>
• ⏳ Pending Commands: <b>{stats['pending_commands']}</b>

⚙️ <b>System Info:</b>
• 🎯 Loaded Commands: <b>{len(COMMAND_HANDLERS)}</b>
• 🕒 Uptime: <i>Since server start</i>
• 💾 Database: <b>Supabase Connected</b>

📊 <b>Commands:</b>
<code>/logs</code> - Your activity
<code>/adminlogs</code> - System logs (Admin)
    """
