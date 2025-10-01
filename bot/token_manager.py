import os
import re
import logging

logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self):
        self.token = os.environ.get('BOT_TOKEN', '')
        logger.info(f"✅ Token loaded: {self.token[:10]}..." if self.token else "❌ No token found")
    
    def inject_token_into_file(self, file_path):
        """Read file and replace YOUR_BOT_TOKEN_HERE with actual token"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace any token placeholder
            original_content = content
            content = content.replace('YOUR_BOT_TOKEN_HERE', self.token)
            content = content.replace('"YOUR_BOT_TOKEN_HERE"', f'"{self.token}"')
            content = content.replace("'YOUR_BOT_TOKEN_HERE'", f"'{self.token}'")
            
            # Also replace common variations
            content = re.sub(r'TOKEN\s*=\s*["\']([^"\']*YOUR_BOT_TOKEN[^"\']*)["\']', 
                           f'TOKEN = "{self.token}"', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                logger.info(f"✅ Token injected into {file_path}")
                return True
            else:
                logger.warning(f"⚠️ No token placeholder found in {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error injecting token into {file_path}: {e}")
            return False
    
    def restore_original_file(self, file_path, original_content):
        """Restore original file content (for cleanup)"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(original_content)
            logger.info(f"✅ Original file restored: {file_path}")
        except Exception as e:
            logger.error(f"❌ Error restoring {file_path}: {e}")
