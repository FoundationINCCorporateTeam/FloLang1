"""std/crypto - Cryptographic primitives module.

This module provides cryptographic functions using secure implementations.
"""

import os
import base64
from typing import Dict, Any, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from argon2.low_level import hash_secret_raw, verify_secret, Type


def random_bytes(n: int) -> bytes:
    """Generate random bytes.
    
    Args:
        n: Number of bytes
    
    Returns:
        Random bytes
    """
    return os.urandom(n)


def argon2id_hash(password: str, params: Optional[Dict[str, int]] = None) -> str:
    """Hash password using Argon2id.
    
    Args:
        password: Password to hash
        params: Optional parameters (memory_cost, time_cost, parallelism)
    
    Returns:
        Encoded hash string
    """
    if params is None:
        params = {
            "memory_cost": 65536,
            "time_cost": 3,
            "parallelism": 4,
        }
    
    salt = os.urandom(16)
    
    hash_bytes = hash_secret_raw(
        secret=password.encode('utf-8'),
        salt=salt,
        time_cost=params.get("time_cost", 3),
        memory_cost=params.get("memory_cost", 65536),
        parallelism=params.get("parallelism", 4),
        hash_len=32,
        type=Type.ID,
    )
    
    # Encode in a simple format: salt$hash (both base64)
    encoded = f"{base64.b64encode(salt).decode()}${base64.b64encode(hash_bytes).decode()}"
    return encoded


def argon2id_verify(hash_str: str, password: str) -> bool:
    """Verify password against Argon2id hash.
    
    Args:
        hash_str: Encoded hash string
        password: Password to verify
    
    Returns:
        True if password matches
    """
    try:
        # Parse the simple format
        parts = hash_str.split('$')
        if len(parts) != 2:
            return False
        
        salt = base64.b64decode(parts[0])
        expected_hash = base64.b64decode(parts[1])
        
        # Recompute hash with same salt
        computed_hash = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID,
        )
        
        return computed_hash == expected_hash
    except Exception:
        return False


def pbkdf2_hash(password: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Hash password using PBKDF2.
    
    Args:
        password: Password to hash
        params: Optional parameters (iterations, algorithm)
    
    Returns:
        Encoded hash string
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    
    if params is None:
        params = {
            "iterations": 100000,
            "algorithm": "sha256",
        }
    
    salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=params.get("iterations", 100000),
    )
    
    hash_bytes = kdf.derive(password.encode('utf-8'))
    
    # Encode in a simple format: salt$hash (both base64)
    encoded = f"{base64.b64encode(salt).decode()}${base64.b64encode(hash_bytes).decode()}"
    return encoded


def aes_gcm_encrypt(key: bytes, nonce: bytes, plaintext: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """Encrypt with AES-256-GCM.
    
    Args:
        key: 32-byte encryption key
        nonce: 12-byte nonce
        plaintext: Data to encrypt
        associated_data: Optional associated data
    
    Returns:
        Ciphertext (includes auth tag)
    """
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(nonce, plaintext, associated_data)


def aes_gcm_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """Decrypt with AES-256-GCM.
    
    Args:
        key: 32-byte encryption key
        nonce: 12-byte nonce
        ciphertext: Data to decrypt
        associated_data: Optional associated data
    
    Returns:
        Plaintext
    """
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data)


def chacha20_encrypt(key: bytes, nonce: bytes, plaintext: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """Encrypt with ChaCha20-Poly1305.
    
    Args:
        key: 32-byte encryption key
        nonce: 12-byte nonce
        plaintext: Data to encrypt
        associated_data: Optional associated data
    
    Returns:
        Ciphertext (includes auth tag)
    """
    cipher = ChaCha20Poly1305(key)
    return cipher.encrypt(nonce, plaintext, associated_data)


def chacha20_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """Decrypt with ChaCha20-Poly1305.
    
    Args:
        key: 32-byte encryption key
        nonce: 12-byte nonce
        ciphertext: Data to decrypt
        associated_data: Optional associated data
    
    Returns:
        Plaintext
    """
    cipher = ChaCha20Poly1305(key)
    return cipher.decrypt(nonce, ciphertext, associated_data)
