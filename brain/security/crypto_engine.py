"""
Crypto Engine - Brain Security Module

This module provides the CryptoEngine class wrapper for the root crypto_engine module.
It delegates to the main crypto_engine.py for actual encryption operations.

Usage:
    from brain.security.crypto_engine import CryptoEngine

    engine = CryptoEngine()
    key = engine.login_with_passphrase(user_id, password)
    if not key:
        key = engine.initialize_user_encryption(user_id, password)
    st.session_state['crypto_key'] = key
📚 REQUIRED READING BEFORE MODIFICATION:
- SECURITY_GUIDE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from typing import Optional
from crypto_engine import (
    encrypt_data,
    decrypt_data,
    login_with_passphrase as _login_with_passphrase,
    initialize_user_encryption as _initialize_user_encryption,
)


class CryptoEngine:
    """
    Crypto engine wrapper for Brain security operations.

    Provides encryption/decryption and user passphrase management.
    """

    def encrypt(self, data):
        """
        Encrypt data using the active encryption mode.

        Args:
            data: Dictionary, string, or bytes to encrypt

        Returns:
            Encrypted data (or plaintext in bypass mode)
        """
        return encrypt_data(data)

    def decrypt(self, data):
        """
        Decrypt data using the active encryption mode.

        Args:
            data: Encrypted data to decrypt

        Returns:
            Decrypted data (or plaintext in bypass mode)
        """
        return decrypt_data(data)

    def login_with_passphrase(self, user_id: int, passphrase: str, conn=None) -> Optional[bytes]:
        """
        Authenticate and derive encryption key from user passphrase.

        Args:
            user_id: User ID
            passphrase: User's passphrase (typically their login password)
            conn: Optional database connection

        Returns:
            bytes: Derived encryption key, or None if user has no salt stored
        """
        return _login_with_passphrase(user_id, passphrase, conn)

    def initialize_user_encryption(self, user_id: int, passphrase: str, conn=None) -> bytes:
        """
        Initialize encryption for a user (first-time setup).

        Args:
            user_id: User ID
            passphrase: User's chosen passphrase
            conn: Optional database connection

        Returns:
            bytes: Derived encryption key

        Raises:
            ValueError: If passphrase is weak or initialization fails
        """
        return _initialize_user_encryption(user_id, passphrase, conn)


# Legacy module-level functions for backward compatibility
def encrypt(data):
    """Legacy function - use CryptoEngine().encrypt() instead."""
    return encrypt_data(data)


def decrypt(data):
    """Legacy function - use CryptoEngine().decrypt() instead."""
    return decrypt_data(data)
