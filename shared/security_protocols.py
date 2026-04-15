import os
import json
import logging
from cryptography.fernet import Fernet
from typing import Dict, Optional

logger = logging.getLogger("SecurityProtocols")

class SecurityManager:
    def __init__(self, key_file: str = "secret.key", api_keys_file: str = "api_keys.enc"):
        self.key_file = key_file
        self.api_keys_file = api_keys_file
        self._fernet = None
        self._initialize_key()

    def _initialize_key(self):
        """Load or generate the encryption key."""
        if not os.path.exists(self.key_file):
            logger.info("Generating new encryption key for API keys.")
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        with open(self.key_file, 'rb') as f:
            key = f.read()
            self._fernet = Fernet(key)

    def encrypt_and_save_keys(self, keys_dict: Dict[str, Dict[str, str]]):
        """Encrypt API keys and store them on disk."""
        data = json.dumps(keys_dict).encode('utf-8')
        encrypted_data = self._fernet.encrypt(data)
        with open(self.api_keys_file, 'wb') as f:
            f.write(encrypted_data)
        logger.info(f"API keys encrypted and saved to {self.api_keys_file}")

    def load_and_decrypt_keys(self) -> Dict[str, Dict[str, str]]:
        """Decrypt and return the API keys."""
        if not os.path.exists(self.api_keys_file):
            logger.warning("No encrypted API keys file found.")
            return {}
        
        try:
            with open(self.api_keys_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to decrypt API keys: {e}")
            return {}

    def whitelist_ip_check(self, allowed_ips: list) -> bool:
        """
        Mock IP validation. 
        In a production VPS environment, this could involve checking the machine's external IP
        against an expected whitelist to ensure the bot hasn't been moved.
        """
        # For simulation, we assume it's valid if allowed_ips are provided.
        if not allowed_ips:
            return False
        return True
