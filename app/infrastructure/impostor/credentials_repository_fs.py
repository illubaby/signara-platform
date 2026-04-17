"""Filesystem-based credentials repository implementation.

Loads encrypted credentials from disk using Fernet encryption.
"""

import json
from pathlib import Path
from typing import Dict
from cryptography.fernet import Fernet


class CredentialsRepositoryFS:
    """Load credentials from encrypted files on filesystem."""
    
    def __init__(self, key_file: Path | None = None, creds_file: Path | None = None):
        """Initialize with file paths.
        
        Args:
            key_file: Path to encryption key file (defaults to ./bin/python/secret.key)
            creds_file: Path to encrypted credentials file (defaults to ./bin/python/credentials.enc)
        """
        if key_file is None:
            key_file = Path("./bin/python/secret.key").resolve()
        if creds_file is None:
            creds_file = Path("./bin/python/credentials.enc").resolve()
        
        self.key_file = key_file
        self.creds_file = creds_file
    
    def load_credentials(self) -> Dict[str, str]:
        """Load and decrypt user credentials.
        
        Returns:
            Dictionary mapping usernames to passwords
            
        Raises:
            FileNotFoundError: If key or credentials file not found
            Exception: If decryption fails
        """
        if not self.key_file.exists():
            raise FileNotFoundError(f"Encryption key not found: {self.key_file}")
        if not self.creds_file.exists():
            raise FileNotFoundError(f"Credentials file not found: {self.creds_file}")
        
        # Load encryption key
        with open(self.key_file, "rb") as f:
            key = f.read()
        
        cipher = Fernet(key)
        
        # Load and decrypt credentials
        with open(self.creds_file, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        credentials = json.loads(decrypted_data)
        
        return credentials
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify that su authentication works for a given username/password.
        
        Args:
            username: The username to su to
            password: The password for authentication
            
        Returns:
            True if credentials are valid
        """
        try:
            import pexpect
            
            # Try a simple whoami command via su
            child = pexpect.spawn(f"su - {username} -c 'whoami'", timeout=5)
            child.expect("Password:")
            child.sendline(password)
            child.expect(pexpect.EOF)
            output = child.before.decode().strip()
            
            # Check if the output contains the expected username
            return username in output or "root" in output
        except Exception:
            return False
