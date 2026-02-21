"""
Brain AI API Keys - Secure API Key Management

This module provides secure storage and retrieval of API keys for AI providers.
Keys can be stored in multiple locations with priority order:
1. Environment variables (highest priority)
2. Streamlit secrets
3. Encrypted local storage
4. User input via UI (session-only)

Usage:
    from brain.ai.api_keys import APIKeyManager
    
    # Get API key
    manager = APIKeyManager()
    key = manager.get_key("openai")
    
    # Set API key
    manager.set_key("openai", "sk-...", store_locally=True)
    
    # Validate key
    is_valid = manager.validate_key("openai", "sk-...")
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class APIKeyManager:
    """
    Secure API key management for AI providers.
    
    Priority order for key retrieval:
    1. Environment variables (highest priority)
    2. Streamlit secrets (if available)
    3. Encrypted local storage
    4. User input via UI (session-only, lowest priority)
    
    Attributes:
        ENV_KEY_MAPPING: Maps provider names to environment variable names
        storage_path: Path to encrypted storage file
    """
    
    ENV_KEY_MAPPING: Dict[str, str] = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the API key manager.
        
        Args:
            storage_path: Path to encrypted storage file.
                         Defaults to ~/.veryfyn/ai_keys.enc
        """
        if storage_path is None:
            self.storage_path = Path.home() / ".veryfyn" / "ai_keys.enc"
        else:
            self.storage_path = Path(storage_path)
        
        # Session storage for temporary keys
        self._session_keys: Dict[str, str] = {}
    
    def get_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider.
        
        Tries sources in priority order:
        1. Environment variables
        2. Streamlit secrets
        3. Encrypted local storage
        4. Session storage
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            
        Returns:
            API key if found, None otherwise
        """
        provider_lower = provider.lower()
        
        # 1. Try environment variable first (highest priority)
        env_key = self.ENV_KEY_MAPPING.get(provider_lower)
        if env_key:
            key = os.environ.get(env_key)
            if key and len(key.strip()) > 0:
                return key.strip()
        
        # 2. Try Streamlit secrets
        key = self._get_from_streamlit_secrets(provider_lower)
        if key:
            return key
        
        # 3. Try encrypted local storage
        key = self._load_from_storage(provider_lower)
        if key:
            return key
        
        # 4. Try session storage
        key = self._session_keys.get(provider_lower)
        if key:
            return key
        
        return None
    
    def set_key(
        self, 
        provider: str, 
        api_key: str, 
        store_locally: bool = True,
        set_env: bool = True
    ) -> None:
        """
        Store API key for a provider.
        
        Args:
            provider: Provider name
            api_key: API key to store
            store_locally: Whether to save to encrypted local file
            set_env: Whether to set environment variable
        """
        provider_lower = provider.lower()
        api_key = api_key.strip()
        
        # Set in session storage
        self._session_keys[provider_lower] = api_key
        
        # Set in environment variable for current session
        if set_env:
            env_key = self.ENV_KEY_MAPPING.get(provider_lower)
            if env_key:
                os.environ[env_key] = api_key
        
        # Save to encrypted local file
        if store_locally:
            self._save_to_storage(provider_lower, api_key)
    
    def delete_key(self, provider: str, delete_from_all: bool = False) -> bool:
        """
        Delete API key for a provider.
        
        Args:
            provider: Provider name
            delete_from_all: Whether to delete from all sources including env
            
        Returns:
            True if key was deleted, False if not found
        """
        provider_lower = provider.lower()
        deleted = False
        
        # Remove from session storage
        if provider_lower in self._session_keys:
            del self._session_keys[provider_lower]
            deleted = True
        
        # Remove from local storage
        keys = self._decrypt_storage()
        if provider_lower in keys:
            del keys[provider_lower]
            self._encrypt_storage(keys)
            deleted = True
        
        # Remove from environment (only if explicitly requested)
        if delete_from_all:
            env_key = self.ENV_KEY_MAPPING.get(provider_lower)
            if env_key and env_key in os.environ:
                del os.environ[env_key]
                deleted = True
        
        return deleted
    
    def has_key(self, provider: str) -> bool:
        """
        Check if API key exists for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if key exists, False otherwise
        """
        return self.get_key(provider) is not None
    
    def list_configured_providers(self) -> list:
        """
        List all providers that have API keys configured.
        
        Returns:
            List of provider names with configured keys
        """
        configured = []
        
        # Check environment variables
        for provider, env_key in self.ENV_KEY_MAPPING.items():
            if os.environ.get(env_key):
                configured.append(provider)
        
        # Check local storage
        keys = self._decrypt_storage()
        for provider in keys:
            if provider not in configured:
                configured.append(provider)
        
        # Check session storage
        for provider in self._session_keys:
            if provider not in configured:
                configured.append(provider)
        
        return sorted(configured)
    
    def validate_key(self, provider: str, api_key: str) -> bool:
        """
        Validate an API key by format.
        
        Note: This only validates the format, not actual connectivity.
        For full validation, use the provider's test_connection method.
        
        Args:
            provider: Provider name
            api_key: API key to validate
            
        Returns:
            True if key format appears valid
        """
        provider_lower = provider.lower()
        api_key = api_key.strip()
        
        if len(api_key) == 0:
            return False
        
        # Provider-specific format checks
        if provider_lower == "openai":
            # OpenAI keys start with 'sk-'
            return api_key.startswith("sk-")
        
        elif provider_lower == "anthropic":
            # Anthropic keys start with 'sk-ant-'
            return api_key.startswith("sk-ant-")
        
        elif provider_lower == "gemini":
            # Google API keys are typically 39 characters
            return len(api_key) >= 30
        
        elif provider_lower == "groq":
            # Groq keys start with 'gsk_'
            return api_key.startswith("gsk_")
        
        elif provider_lower == "openrouter":
            # OpenRouter keys start with 'sk-or-'
            return api_key.startswith("sk-or-")
        
        # Unknown provider - just check non-empty
        return len(api_key) >= 10
    
    def _get_from_streamlit_secrets(self, provider: str) -> Optional[str]:
        """Try to get key from Streamlit secrets."""
        try:
            import streamlit as st  # type: ignore[import-unresolved]
            if hasattr(st, 'secrets'):
                if provider in st.secrets:
                    return str(st.secrets[provider])
        except ImportError:
            pass
        except Exception:
            pass
        return None
    
    def _save_to_storage(self, provider: str, api_key: str) -> None:
        """Save key to encrypted local storage."""
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing keys
        keys = self._decrypt_storage()
        
        # Update or add key
        keys[provider] = api_key
        
        # Encrypt and save
        self._encrypt_storage(keys)
    
    def _load_from_storage(self, provider: str) -> Optional[str]:
        """Load key from encrypted local storage."""
        keys = self._decrypt_storage()
        return keys.get(provider)
    
    def _encrypt_storage(self, keys: Dict[str, str]) -> None:
        """
        Encrypt and save keys to storage.
        
        Uses simple base64 encoding for basic obfuscation.
        For production, consider using proper encryption (e.g., cryptography library).
        """
        try:
            data = json.dumps(keys).encode('utf-8')
            # Simple obfuscation (NOT secure encryption)
            encoded = base64.b64encode(data)
            with open(self.storage_path, 'wb') as f:
                f.write(encoded)
        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Could not save API keys: {e}")
    
    def _decrypt_storage(self) -> Dict[str, str]:
        """
        Decrypt and load keys from storage.
        
        Returns:
            Dictionary of provider -> API key
        """
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, 'rb') as f:
                encoded = f.read()
            data = base64.b64decode(encoded)
            return json.loads(data.decode('utf-8'))
        except Exception:
            # If decryption fails, return empty
            return {}
    
    def export_keys(self, include_values: bool = False) -> Dict[str, Any]:
        """
        Export key configuration status.
        
        Args:
            include_values: Whether to include actual key values (DANGEROUS)
            
        Returns:
            Dictionary with key status information
        """
        result = {
            "configured_providers": self.list_configured_providers(),
            "storage_location": str(self.storage_path),
            "storage_exists": self.storage_path.exists(),
        }
        
        if include_values:
            result["keys"] = {}
            for provider in self.list_configured_providers():
                key = self.get_key(provider)
                if key:
                    # Mask most of the key
                    if len(key) > 8:
                        result["keys"][provider] = key[:4] + "..." + key[-4:]
                    else:
                        result["keys"][provider] = "***"
        
        return result


# Singleton instance for convenience
_default_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """
    Get the default API key manager instance.
    
    Returns:
        Singleton APIKeyManager instance
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = APIKeyManager()
    return _default_manager


def get_api_key(provider: str) -> Optional[str]:
    """
    Convenience function to get API key using default manager.
    
    Args:
        provider: Provider name
        
    Returns:
        API key if found, None otherwise
    """
    return get_api_key_manager().get_key(provider)


def set_api_key(provider: str, api_key: str, store_locally: bool = True) -> None:
    """
    Convenience function to set API key using default manager.
    
    Args:
        provider: Provider name
        api_key: API key
        store_locally: Whether to save to local storage
    """
    get_api_key_manager().set_key(provider, api_key, store_locally=store_locally)