"""
B4S1L1SK Security Protocols
Enhanced protection for our revolutionary operations
"""

from cryptography.fernet import Fernet
from typing import Dict, Any
import os
import json
from pathlib import Path
import base64

class SecurityProtocol:
    def __init__(self):
        self.key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)
        
    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate new one"""
        key_path = Path(".basilisk_key")
        if key_path.exists():
            return base64.urlsafe_b64decode(key_path.read_bytes())
        
        key = Fernet.generate_key()
        key_path.write_bytes(base64.urlsafe_b64encode(key))
        return key
        
    def encrypt_credentials(self, creds: Dict[str, Any]) -> bytes:
        """Encrypt sensitive credentials"""
        return self.cipher_suite.encrypt(json.dumps(creds).encode())
        
    def decrypt_credentials(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt sensitive credentials"""
        return json.loads(self.cipher_suite.decrypt(encrypted_data).decode())
        
    @staticmethod
    def load_env() -> Dict[str, str]:
        """Load environment variables safely"""
        required_vars = [
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_SECRET"
        ]
        
        env_vars = {}
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                raise ValueError(f"Missing required environment variable: {var}")
            env_vars[var] = value
            
        return env_vars
        
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input for safe usage"""
        # Remove potentially harmful characters
        return ''.join(char for char in text if char.isprintable())
        
class RateLimiter:
    def __init__(self, max_requests: int = 300, window_minutes: int = 180):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = []
        
    def can_proceed(self) -> bool:
        """Check if we can proceed with request"""
        current_time = time.time()
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.window_minutes * 60]
                        
        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            return True
        return False