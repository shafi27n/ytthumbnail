from flask import Flask, request, jsonify
import os
import logging
import importlib
import pkgutil
from datetime import datetime
import threading
import subprocess
import sys
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import token manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from token_manager import TokenManager

class HandlerManager:
    def __init__(self):
        self.token_manager = TokenManager()
        self.handler_processes = {}
        self.handler_files = {}
    
    def discover_handlers(self):
        """Discover all handler files in handlers directory"""
        handlers_dir = os.path.join(os.path.dirname(__file__), 'handlers')
        handlers = {}
        
        try:
            for filename in os.listdir(handlers_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    handler_name = filename[:-3]  # Remove .py extension
                    handler_path = os.path.join(handlers_dir, filename)
                    handlers[handler_name] = handler_path
                    logger.info(f"📁 Discovered handler: {handler_name}")
        
        except Exception as e:
            logger.error(f"❌ Error discovering handlers: {e}")
        
        return handlers
    
    def start_handler(self, handler_name, handler_path):
        """Start a handler in a separate process with token injection"""
        try:
            # Read original content for later restoration
            with open(handler_path, 'r', encoding='utf-8') as file:
                original_content = file.read()
            
            # Inject token
            self.token_manager.inject_token_into_file(handler_path)
            
            # Start the handler in a separate process
            process = subprocess.Popen([
                sys.executable, handler_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.handler_processes[handler_name] = process
            self.handler_files[handler_name] = {
                'path': handler_path,
                'original_content': original_content
            }
            
            logger.info(f"🚀 Started handler: {handler_name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start handler {handler_name}: {e}")
            return False
    
    def start_all_handlers(self):
        """Start all discovered handlers"""
        handlers = self.discover_handlers()
        
        if not handlers:
            logger.warning("⚠️ No handlers found")
            return
        
        for handler_name, handler_path in handlers.items():
            self.start_handler(handler_name, handler_path)
        
        logger.info(f"🎯 Total handlers started: {len(handlers)}")
    
    def stop_all_handlers(self):
        """Stop all running handlers and restore original files"""
        for handler_name, process in self.handler_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"🛑 Stopped handler: {handler_name}")
            except Exception as e:
                logger.error(f"❌ Error stopping {handler_name}: {e}")
        
        # Restore original files
        for handler_name, file_info in self.handler_files.items():
            self.token_manager.restore_original_file(
                file_info['path'], 
                file_info['original_content']
            )
        
        self.handler_processes.clear()
        self.handler_files.clear()

# Global handler manager
handler_manager = HandlerManager()

@app.route('/', methods=['GET', 'POST'])
def handle_webhook():
    """Main webhook endpoint"""
    try:
        if request.method == 'GET':
            return jsonify({
                'status': 'Bot is running with DYNAMIC TOKEN INJECTION system',
                'active_handlers': list(handler_manager.handler_processes.keys()),
                'total_handlers': len(handler_manager.handler_processes),
                'timestamp': datetime.now().isoformat()
            })

        if request.method == 'POST':
            # For webhook messages, just acknowledge
            return jsonify({'ok': True})

    except Exception as e:
        logger.error(f'Webhook error: {e}')
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    handler_status = {}
    for handler_name, process in handler_manager.handler_processes.items():
        handler_status[handler_name] = {
            'pid': process.pid,
            'alive': process.poll() is None
        }
    
    return jsonify({
        'status': 'healthy',
        'active_handlers': len(handler_manager.handler_processes),
        'handler_status': handler_status,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/restart/<handler_name>')
def restart_handler(handler_name):
    """Restart a specific handler"""
    if handler_name in handler_manager.handler_processes:
        # Stop current process
        handler_manager.handler_processes[handler_name].terminate()
        
        # Restart
        handler_path = handler_manager.handler_files[handler_name]['path']
        handler_manager.start_handler(handler_name, handler_path)
        
        return jsonify({'status': f'Handler {handler_name} restarted'})
    else:
        return jsonify({'error': 'Handler not found'}), 404

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Shutdown signal received")
    handler_manager.stop_all_handlers()
    sys.exit(0)

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start all handlers
    logger.info("🤖 Starting all handlers...")
    handler_manager.start_all_handlers()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🌐 Web server starting on port {port}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    finally:
        # Cleanup on exit
        handler_manager.stop_all_handlers()
