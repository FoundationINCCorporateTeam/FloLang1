"""Mnstor - Encrypted secrets storage for Flo.

Implements AES-256-GCM encryption with Argon2id key derivation.
"""

import json
import base64
import os
from typing import Dict, Any, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type


class MnstorError(Exception):
    """Error in mnstor operations."""
    pass


class Mnstor:
    """Encrypted secrets storage."""
    
    DEFAULT_KDF_PARAMS = {
        "memory_cost": 65536,  # 64 MB
        "time_cost": 3,
        "parallelism": 4,
    }
    
    @staticmethod
    def derive_key(password: str, salt: bytes, kdf_params: Optional[Dict[str, int]] = None) -> bytes:
        """Derive encryption key from password using Argon2id.
        
        Args:
            password: Password string
            salt: Salt bytes
            kdf_params: KDF parameters (memory_cost, time_cost, parallelism)
        
        Returns:
            32-byte encryption key
        """
        if kdf_params is None:
            kdf_params = Mnstor.DEFAULT_KDF_PARAMS
        
        key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=kdf_params.get("time_cost", 3),
            memory_cost=kdf_params.get("memory_cost", 65536),
            parallelism=kdf_params.get("parallelism", 4),
            hash_len=32,
            type=Type.ID,
        )
        
        return key
    
    @staticmethod
    def encrypt(data: Dict[str, str], password: str, kdf_params: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Encrypt secrets data.
        
        Args:
            data: Dictionary of secrets
            password: Encryption password
            kdf_params: KDF parameters
        
        Returns:
            Encrypted envelope
        """
        if kdf_params is None:
            kdf_params = Mnstor.DEFAULT_KDF_PARAMS
        
        # Generate random salt and nonce
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        # Derive encryption key
        key = Mnstor.derive_key(password, salt, kdf_params)
        
        # Serialize data
        plaintext = json.dumps(data).encode('utf-8')
        
        # Encrypt with AES-256-GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Create envelope
        envelope = {
            "version": "1.0",
            "kdf": "argon2id",
            "kdf_params": {
                "memory_cost": kdf_params.get("memory_cost", 65536),
                "time_cost": kdf_params.get("time_cost", 3),
                "parallelism": kdf_params.get("parallelism", 4),
                "salt": base64.b64encode(salt).decode('utf-8'),
            },
            "cipher": "aes-256-gcm",
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        }
        
        return envelope
    
    @staticmethod
    def decrypt(envelope: Dict[str, Any], password: str) -> Dict[str, str]:
        """Decrypt secrets data.
        
        Args:
            envelope: Encrypted envelope
            password: Decryption password
        
        Returns:
            Decrypted secrets dictionary
        
        Raises:
            MnstorError: On decryption failure
        """
        try:
            # Validate version
            if envelope.get("version") != "1.0":
                raise MnstorError(f"Unsupported version: {envelope.get('version')}")
            
            # Validate cipher
            if envelope.get("cipher") != "aes-256-gcm":
                raise MnstorError(f"Unsupported cipher: {envelope.get('cipher')}")
            
            # Extract KDF params
            kdf_params = envelope["kdf_params"]
            salt = base64.b64decode(kdf_params["salt"])
            
            params = {
                "memory_cost": kdf_params["memory_cost"],
                "time_cost": kdf_params["time_cost"],
                "parallelism": kdf_params["parallelism"],
            }
            
            # Derive key
            key = Mnstor.derive_key(password, salt, params)
            
            # Extract ciphertext and nonce
            nonce = base64.b64decode(envelope["nonce"])
            ciphertext = base64.b64decode(envelope["ciphertext"])
            
            # Decrypt
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            # Parse JSON
            data = json.loads(plaintext.decode('utf-8'))
            
            return data
        
        except Exception as e:
            raise MnstorError(f"Decryption failed: {e}")
    
    @staticmethod
    def save(filepath: str, data: Dict[str, str], password: str, kdf_params: Optional[Dict[str, int]] = None):
        """Save encrypted secrets to file.
        
        Args:
            filepath: Path to save file
            data: Secrets dictionary
            password: Encryption password
            kdf_params: KDF parameters
        """
        envelope = Mnstor.encrypt(data, password, kdf_params)
        
        with open(filepath, 'w') as f:
            json.dump(envelope, f, indent=2)
    
    @staticmethod
    def load(filepath: str, password: str) -> Dict[str, str]:
        """Load encrypted secrets from file.
        
        Args:
            filepath: Path to secrets file
            password: Decryption password
        
        Returns:
            Decrypted secrets dictionary
        """
        with open(filepath, 'r') as f:
            envelope = json.load(f)
        
        return Mnstor.decrypt(envelope, password)
    
    @staticmethod
    def get(filepath: str, key: str, password: str) -> Optional[str]:
        """Get a specific secret from file.
        
        Args:
            filepath: Path to secrets file
            key: Secret key
            password: Decryption password
        
        Returns:
            Secret value or None if not found
        """
        data = Mnstor.load(filepath, password)
        return data.get(key)


# Global instance for easy access
_default_mnstor: Optional[Dict[str, str]] = None
_default_password: Optional[str] = None


def configure(filepath: str, password: str):
    """Configure default mnstor file.
    
    Args:
        filepath: Path to secrets file
        password: Decryption password
    """
    global _default_mnstor, _default_password
    _default_mnstor = Mnstor.load(filepath, password)
    _default_password = password


def get(key: str) -> Optional[str]:
    """Get secret from default mnstor.
    
    Args:
        key: Secret key
    
    Returns:
        Secret value or None
    """
    if _default_mnstor is None:
        return None
    return _default_mnstor.get(key)
