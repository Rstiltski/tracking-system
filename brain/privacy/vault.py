"""
PII Vault - Phase 7.2: Secure Storage

Secure storage and retrieval of token-to-PII mappings with:
- Encryption at rest (optional)
- Access control and audit logging
- Session-based token management
- Automatic expiry of old tokens

The vault ensures that:
1. Token mappings are stored securely in the database
2. All vault access is logged for audit
3. Tokens can be looked up efficiently
4. Old mappings can be cleaned up automatically
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

import sqlite3
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .tokenizer import Token, TokenType


@dataclass
class VaultEntry:
    """Represents an entry in the PII vault"""
    id: Optional[int] = None
    token_id: str = ""
    token_type: str = ""
    encrypted_value: str = ""  # In production, this should be encrypted
    context: Optional[str] = None
    session_id: Optional[str] = None
    company_id: int = 1
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    accessed_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.accessed_at:
            data['accessed_at'] = self.accessed_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data


class PIIVault:
    """
    Secure vault for storing token-to-PII mappings.
    
    Example:
        vault = PIIVault(conn, company_id=1, user_id=5)
        
        # Store tokens from tokenization
        session_id = vault.store_tokens(tokens, session_ttl_hours=24)
        
        # Later, retrieve original values
        original_value = vault.get_value("CUST_A", session_id)
        
        # Or retrieve all tokens from a session
        all_tokens = vault.get_session_tokens(session_id)
    """
    
    def __init__(self, conn: sqlite3.Connection, company_id: int = 1, user_id: Optional[int] = None):
        """
        Initialize PII Vault.
        
        Args:
            conn: Database connection
            company_id: Company ID for multi-tenant isolation
            user_id: User ID for audit logging
        """
        self.conn = conn
        self.company_id = company_id
        self.user_id = user_id
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Create vault tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # PII Vault table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brain_pii_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id VARCHAR(50) NOT NULL,
                token_type VARCHAR(20) NOT NULL,
                encrypted_value TEXT NOT NULL,
                context TEXT,
                session_id VARCHAR(100),
                company_id INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP,
                expires_at TIMESTAMP,
                accessed_count INTEGER DEFAULT 0,
                UNIQUE(token_id, session_id, company_id)
            )
        """)
        
        # Vault access audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brain_pii_vault_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vault_entry_id INTEGER,
                token_id VARCHAR(50),
                operation VARCHAR(20) NOT NULL,
                user_id INTEGER,
                company_id INTEGER NOT NULL,
                ip_address VARCHAR(50),
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                FOREIGN KEY (vault_entry_id) REFERENCES brain_pii_vault(id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vault_token_session 
            ON brain_pii_vault(token_id, session_id, company_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vault_session_company 
            ON brain_pii_vault(session_id, company_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vault_expires 
            ON brain_pii_vault(expires_at)
        """)
        
        self.conn.commit()
    
    def generate_session_id(self, context: Optional[str] = None) -> str:
        """
        Generate a unique session ID for a tokenization session.
        
        Args:
            context: Optional context string to include in session ID
            
        Returns:
            Unique session ID string
        """
        timestamp = datetime.now().isoformat()
        data = f"{timestamp}:{self.company_id}:{self.user_id}:{context or ''}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def store_tokens(
        self, 
        tokens: List[Token], 
        session_id: Optional[str] = None,
        session_ttl_hours: int = 24
    ) -> str:
        """
        Store a list of tokens in the vault.
        
        Args:
            tokens: List of tokens to store
            session_id: Optional session ID (generated if not provided)
            session_ttl_hours: How many hours before tokens expire
            
        Returns:
            Session ID for retrieving tokens later
        """
        if not session_id:
            session_id = self.generate_session_id()
        
        expires_at = datetime.now() + timedelta(hours=session_ttl_hours)
        cursor = self.conn.cursor()
        
        for token in tokens:
            # In production, encrypt the original_value
            # For now, we'll just store it as-is (Phase 7.2b will add encryption)
            encrypted_value = self._encrypt_value(token.original_value)
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO brain_pii_vault 
                    (token_id, token_type, encrypted_value, context, session_id, 
                     company_id, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    token.token_id,
                    token.token_type.value,
                    encrypted_value,
                    token.context,
                    session_id,
                    self.company_id,
                    token.created_at or datetime.now(),
                    expires_at
                ))
                
                vault_entry_id = cursor.lastrowid
                
                # Audit log
                self._log_access(
                    vault_entry_id=vault_entry_id,
                    token_id=token.token_id,
                    operation="STORE",
                    success=True
                )
            
            except sqlite3.Error as e:
                self._log_access(
                    token_id=token.token_id,
                    operation="STORE",
                    success=False,
                    error_message=str(e)
                )
                raise
        
        self.conn.commit()
        return session_id
    
    def get_value(self, token_id: str, session_id: Optional[str] = None) -> Optional[str]:
        """
        Retrieve the original PII value for a token.
        
        Args:
            token_id: Token ID to look up
            session_id: Optional session ID (required for session-scoped tokens)
            
        Returns:
            Original PII value, or None if not found/expired
        """
        cursor = self.conn.cursor()
        
        # Build query
        if session_id:
            query = """
                SELECT id, encrypted_value, accessed_count, expires_at 
                FROM brain_pii_vault
                WHERE token_id = ? AND session_id = ? AND company_id = ?
            """
            params = (token_id, session_id, self.company_id)
        else:
            # Global token (not session-scoped)
            query = """
                SELECT id, encrypted_value, accessed_count, expires_at 
                FROM brain_pii_vault
                WHERE token_id = ? AND session_id IS NULL AND company_id = ?
            """
            params = (token_id, self.company_id)
        
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if not row:
                self._log_access(
                    token_id=token_id,
                    operation="RETRIEVE",
                    success=False,
                    error_message="Token not found"
                )
                return None
            
            entry_id, encrypted_value, accessed_count, expires_at = row
            
            # Check expiry
            if expires_at:
                expires_dt = datetime.fromisoformat(expires_at)
                if datetime.now() > expires_dt:
                    self._log_access(
                        vault_entry_id=entry_id,
                        token_id=token_id,
                        operation="RETRIEVE",
                        success=False,
                        error_message="Token expired"
                    )
                    return None
            
            # Update access tracking
            cursor.execute("""
                UPDATE brain_pii_vault 
                SET accessed_at = ?, accessed_count = ?
                WHERE id = ?
            """, (datetime.now(), accessed_count + 1, entry_id))
            self.conn.commit()
            
            # Decrypt and return
            original_value = self._decrypt_value(encrypted_value)
            
            self._log_access(
                vault_entry_id=entry_id,
                token_id=token_id,
                operation="RETRIEVE",
                success=True
            )
            
            return original_value
        
        except sqlite3.Error as e:
            self._log_access(
                token_id=token_id,
                operation="RETRIEVE",
                success=False,
                error_message=str(e)
            )
            return None
    
    def get_session_tokens(self, session_id: str) -> List[Token]:
        """
        Retrieve all tokens from a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of Token objects
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT token_id, token_type, encrypted_value, context, created_at
            FROM brain_pii_vault
            WHERE session_id = ? AND company_id = ?
            AND (expires_at IS NULL OR expires_at > ?)
        """, (session_id, self.company_id, datetime.now()))
        
        tokens = []
        for row in cursor.fetchall():
            token_id, token_type_str, encrypted_value, context, created_at = row
            
            token = Token(
                token_id=token_id,
                token_type=TokenType(token_type_str),
                original_value=self._decrypt_value(encrypted_value),
                context=context,
                created_at=datetime.fromisoformat(created_at) if created_at else None
            )
            tokens.append(token)
        
        return tokens
    
    def cleanup_expired(self) -> int:
        """
        Remove expired tokens from the vault.
        
        Returns:
            Number of tokens removed
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM brain_pii_vault
            WHERE expires_at IS NOT NULL AND expires_at <= ?
        """, (datetime.now(),))
        
        deleted_count = cursor.rowcount
        self.conn.commit()
        
        if deleted_count > 0:
            self._log_access(
                operation="CLEANUP",
                success=True,
                error_message=f"Removed {deleted_count} expired tokens"
            )
        
        return deleted_count
    
    def _encrypt_value(self, value: str) -> str:
        """
        Encrypt a PII value for storage using Fernet (AES-128-CBC).
        
        Uses cryptography.fernet for secure encryption:
        - AES-128 in CBC mode with PKCS7 padding
        - HMAC for authentication
        - Key stored in environment variable (ENCRYPTION_KEY)
        - Timestamp for key rotation support
        
        Args:
            value: Plain text value to encrypt
            
        Returns:
            Base64-encoded encrypted value
        """
        if not value:
            return value
        
        try:
            from cryptography.fernet import Fernet
            import os
            
            # Get encryption key from environment
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                # In production, this is an error
                from config import get_config
                config = get_config()
                if config.ENVIRONMENT == "production":
                    raise ValueError("ENCRYPTION_KEY not set - encryption failed")
                # Fallback to base64 for backwards compatibility in development
                import base64
                return base64.b64encode(value.encode()).decode()
            
            # Create Fernet cipher
            fernet = Fernet(key.encode())
            
            # Encrypt the value
            encrypted = fernet.encrypt(value.encode())
            return encrypted.decode()
        
        except ImportError:
            # Cryptography not installed - only allow in development
            from config import get_config
            config = get_config()
            if config.ENVIRONMENT == "production":
                raise ImportError("cryptography library required in production")
            import base64
            return base64.b64encode(value.encode()).decode()
        except Exception as e:
            # Log error but don't crash in development
            from config import get_config
            config = get_config()
            if config.ENVIRONMENT == "production":
                raise ValueError(f"Encryption failed: {e}")
            print(f"Warning: Encryption failed: {e}. Falling back to base64.")
            import base64
            return base64.b64encode(value.encode()).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """
        Decrypt a PII value from storage using Fernet.
        
        Supports both Fernet and base64 for backwards compatibility.
        
        Args:
            encrypted_value: Encrypted value to decrypt
            
        Returns:
            Decrypted plain text value
        """
        if not encrypted_value:
            return encrypted_value
        
        try:
            from cryptography.fernet import Fernet, InvalidToken
            import os
            
            # Get encryption key from environment
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                # Try base64 decode for backwards compatibility (development only)
                from config import get_config
                config = get_config()
                if config.ENVIRONMENT == "production":
                    raise ValueError("ENCRYPTION_KEY not set - decryption failed")
                import base64
                return base64.b64decode(encrypted_value.encode()).decode()
            
            # Create Fernet cipher
            fernet = Fernet(key.encode())
            
            # Try Fernet decryption first
            try:
                decrypted = fernet.decrypt(encrypted_value.encode())
                return decrypted.decode()
            except InvalidToken:
                # Not Fernet encrypted - try base64 (development backwards compatibility)
                from config import get_config
                config = get_config()
                if config.ENVIRONMENT == "production":
                    raise ValueError("Invalid encrypted data - decryption failed")
                import base64
                return base64.b64decode(encrypted_value.encode()).decode()
        
        except ImportError:
            # Cryptography not installed - only allow in development
            from config import get_config
            config = get_config()
            if config.ENVIRONMENT == "production":
                raise ImportError("cryptography library required in production")
            import base64
            return base64.b64decode(encrypted_value.encode()).decode()
        except Exception as e:
            # Log error but return encrypted value to avoid data loss in development
            from config import get_config
            config = get_config()
            if config.ENVIRONMENT == "production":
                raise ValueError(f"Decryption failed: {e}")
            print(f"Warning: Decryption failed: {e}. Returning encrypted value.")
            return encrypted_value
    
    def _log_access(
        self,
        vault_entry_id: Optional[int] = None,
        token_id: Optional[str] = None,
        operation: str = "",
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log vault access to audit table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO brain_pii_vault_audit 
            (vault_entry_id, token_id, operation, user_id, company_id, 
             accessed_at, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vault_entry_id,
            token_id,
            operation,
            self.user_id,
            self.company_id,
            datetime.now(),
            success,
            error_message
        ))
        self.conn.commit()
    
    def get_audit_log(self, token_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Retrieve audit log for vault access.
        
        Args:
            token_id: Optional token ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of audit log entries
        """
        cursor = self.conn.cursor()
        
        if token_id:
            cursor.execute("""
                SELECT id, token_id, operation, user_id, accessed_at, success, error_message
                FROM brain_pii_vault_audit
                WHERE token_id = ? AND company_id = ?
                ORDER BY accessed_at DESC
                LIMIT ?
            """, (token_id, self.company_id, limit))
        else:
            cursor.execute("""
                SELECT id, token_id, operation, user_id, accessed_at, success, error_message
                FROM brain_pii_vault_audit
                WHERE company_id = ?
                ORDER BY accessed_at DESC
                LIMIT ?
            """, (self.company_id, limit))
        
        logs = []
        for row in cursor.fetchall():
            log_id, token_id, operation, user_id, accessed_at, success, error_message = row
            logs.append({
                'id': log_id,
                'token_id': token_id,
                'operation': operation,
                'user_id': user_id,
                'accessed_at': accessed_at,
                'success': bool(success),
                'error_message': error_message
            })
        
        return logs


class EncryptionVault:
    """
    Simple encryption vault for PII fields in the database.
    
    Phase 7.1: Field-Level Encryption
    
    Uses Fernet (AES-128-CBC) for symmetric encryption of PII at rest.
    Key is stored in ENCRYPTION_KEY environment variable.
    
    Example:
        vault = EncryptionVault()
        
        # Encrypt before storing
        encrypted_email = vault.encrypt("user@example.com")
        
        # Decrypt when retrieving
        plain_email = vault.decrypt(encrypted_email)
    """
    
    def __init__(self):
        """
        Initialize encryption vault with key from environment.
        
        Raises:
            ValueError: If ENCRYPTION_KEY not set in environment (production mode)
        """
        import os
        from config import get_config
        
        config = get_config()
        self.key = os.getenv('ENCRYPTION_KEY')
        
        # In production, encryption key is mandatory
        if config.ENVIRONMENT == "production" and not self.key:
            raise ValueError("ENCRYPTION_KEY environment variable must be set in production. Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
        
        self._fernet = None
    
    def _get_fernet(self):
        """Lazy load Fernet cipher"""
        if self._fernet is None and self.key:
            try:
                from cryptography.fernet import Fernet
                self._fernet = Fernet(self.key.encode())
            except ImportError:
                pass  # Cryptography not installed
        return self._fernet
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.
        
        Args:
            plaintext: Plain text to encrypt
            
        Returns:
            Base64-encoded encrypted value
        """
        if not plaintext:
            return plaintext
        
        fernet = self._get_fernet()
        if fernet:
            try:
                return fernet.encrypt(plaintext.encode()).decode()
            except Exception as e:
                print(f"Warning: Encryption failed: {e}")
        
        # Fallback to base64 if encryption not available
        import base64
        return base64.b64encode(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted value.
        
        Args:
            ciphertext: Encrypted value to decrypt
            
        Returns:
            Decrypted plain text
        """
        if not ciphertext:
            return ciphertext
        
        fernet = self._get_fernet()
        if fernet:
            try:
                from cryptography.fernet import InvalidToken
                return fernet.decrypt(ciphertext.encode()).decode()
            except InvalidToken:
                # Not Fernet encrypted - try base64
                pass
            except Exception as e:
                print(f"Warning: Decryption failed: {e}")
        
        # Fallback to base64 decode
        try:
            import base64
            return base64.b64decode(ciphertext.encode()).decode()
        except Exception:
            # Return as-is if decryption fails
            return ciphertext
    
    def encrypt_if_needed(self, value: str) -> str:
        """
        Encrypt value if it's not already encrypted.
        
        Checks if value is already Fernet-encrypted by attempting decrypt.
        
        Args:
            value: Value that may or may not be encrypted
            
        Returns:
            Encrypted value
        """
        if not value:
            return value
        
        # Try to decrypt - if it works, already encrypted
        try:
            decrypted = self.decrypt(value)
            # If decrypt succeeded and value changed, it was encrypted
            if decrypted != value:
                return value
        except Exception:
            pass
        
        # Not encrypted - encrypt it
        return self.encrypt(value)
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64-encoded encryption key
        """
        try:
            from cryptography.fernet import Fernet
            return Fernet.generate_key().decode()
        except ImportError:
            raise ImportError("cryptography library required. Install with: pip install cryptography>=41.0.0")


# ============================================================================
# Global Encryption Vault Instance & Convenience Functions
# ============================================================================

import threading

_encryption_vault = None
_vault_lock = threading.RLock()


def get_encryption_vault():
    """
    Get or create encryption vault for PII protection.
    Returns None if encryption not available.

    This function is safe to call multiple times - it returns the same instance.
    """
    global _encryption_vault

    if _encryption_vault is None:
        with _vault_lock:
            # Double-check after acquiring lock
            if _encryption_vault is None:
                try:
                    _encryption_vault = EncryptionVault()
                except Exception as e:
                    # Log error but don't crash - PII will not be encrypted
                    print(f"Warning: Failed to initialize encryption vault: {e}")
                    return None

    return _encryption_vault


def encrypt_pii(value: str) -> str:
    """
    Encrypt PII field value before storing in database.
    Falls back to plain text if encryption not available.

    Args:
        value: Plain text value to encrypt

    Returns:
        Encrypted value or original value if encryption unavailable
    """
    if not value:
        return value

    vault = get_encryption_vault()
    if vault:
        try:
            return vault.encrypt(value)
        except Exception as e:
            print(f"Warning: PII encryption failed: {e}")

    return value


def decrypt_pii(value: str) -> str:
    """
    Decrypt PII field value after reading from database.
    Falls back to returning encrypted value if decryption fails.

    Args:
        value: Encrypted value to decrypt

    Returns:
        Decrypted value or original value if decryption unavailable
    """
    if not value:
        return value

    vault = get_encryption_vault()
    if vault:
        try:
            return vault.decrypt(value)
        except Exception as e:
            print(f"Warning: PII decryption failed: {e}")

    return value
