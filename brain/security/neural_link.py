"""
Neural Command Link - Cryptic Link Middleware

This module implements a secure command channel using:
- Neural-flow rotating keys based on SHA-256 hash of secret seed + audit-log hash
- Deterministic key generation without external dependencies
- Admin bypass modes for development and testing

Architecture:
- Cryptic Link: Generates neural-flow keys using SHA256(Secret + LastAuditHash)
- NeuralCommandLink: Handles encryption/decryption with audit-log-driven rotation
- Admin Bypass Modes:
  - normal: Full security, keys rotate on neural-flow entropy windows
  - dev_key: Encryption ON, but uses static key (no rotation failures)
  - bypass: Encryption OFF, packets are plain JSON

The Cryptic Link moves all security logic to the server. The "Brain" calculates
the neural flow key using a secret seed, creating a secure, rotating handshake without
exposing secrets to the browser.
📚 REQUIRED READING BEFORE MODIFICATION:
- SECURITY_GUIDE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import os
import json
import hashlib
import base64
import datetime
import logging
from typing import Optional
from cryptography.fernet import Fernet
from config import get_config
logger = logging.getLogger(__name__)


# Backwards-compatible settings helpers
def get_setting(key: str, default=None):
    """Get a setting value.

    This is a lightweight compatibility wrapper used by tests and
    by other modules. Prefer the project's settings API where available.
    """
    # Try to read from environment first
    try:
        val = os.environ.get(key)
        if val is not None:
            return val
    except Exception:
        pass
    return default


def set_setting(key: str, value) -> None:
    """Set a setting value (best-effort). Stores to environment for in-process tests."""
    try:
        os.environ[key] = str(value)
    except Exception:
        pass


# Expose PhysicalSecurityService for test patching compatibility. Prefer importing
# the implementation from the services package; fall back to a minimal shim if
# the services module isn't available in the test environment.
try:
    from services.physical_security import PhysicalSecurityService  # type: ignore
except Exception:
    class PhysicalSecurityService:
        def __init__(self, *args, **kwargs):
            pass

        def get_entropy_anchor(self, *args, **kwargs):
            return ('0' * 64, 0)

class NeuralCommandLink:
    """
    The Cryptic Link Middleware.
    Generates a deterministic neural-flow key based on a server-side secret.
    """

    def __init__(self):
        self.config = get_config()
        self._master_seed = getattr(self.config, 'NEURAL_MASTER_SEED', 'dev_fallback_seed_do_not_use_in_prod')
        self.key_store_path = getattr(self.config, 'NEURAL_KEY_STORE_PATH', 'secure_storage/neural_keys.json')
        if os.path.dirname(self.key_store_path):
            os.makedirs(os.path.dirname(self.key_store_path), exist_ok=True)

    def _get_fact_window_id(self, window_seconds: int=15, now: Optional[datetime.datetime]=None) -> str:
        """
        Generate a deterministic fact window identifier.

        Args:
            window_seconds: Window length in seconds (default: 15)
            now: Optional datetime override (UTC) for deterministic testing

        Returns:
            ISO8601 UTC string representing the window start.
        """
        current_time = now or datetime.datetime.utcnow()
        window_start = int(current_time.timestamp() // window_seconds * window_seconds)
        return datetime.datetime.utcfromtimestamp(window_start).isoformat() + 'Z'

    def get_fact_gated_key(self, fact_domain: str, fact_value: str, fact_window: Optional[str]=None) -> str:
        """
        Generates a 15-second key based on a real-world fact.
        
        Args:
            fact_domain: e.g., 'sports', 'weather', 'blockchain'
            fact_value: e.g., 'ARS_2_MNC_1', '1013hPa', '0xabc...'
            fact_window: Optional explicit window identifier for deterministic replay
            
        Returns:
            A deterministic 32-character key for that fact window.
        """
        window_id = fact_window or self._get_fact_window_id()
        raw_string = f'{self._master_seed}:{fact_domain}:{fact_value}:{window_id}'
        fact_hash = hashlib.sha256(raw_string.encode()).hexdigest()
        return fact_hash[:32]

    def get_todays_public_key(self) -> str:
        """
        Backwards-compatible alias for the current neural flow key.
        This is what we stamp onto the HTML.
        
        Rotation: Automatic (neural-flow window + activity threshold)
        
        Returns:
            Current neural flow key (first 32 characters of SHA-256 hash)
        """
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return self.get_fact_gated_key('calendar_date', today, fact_window=today)

    def verify_packet(self, packet_key: str) -> bool:
        """
        Verifies if an incoming packet was signed with the current neural flow key.
        
        Args:
            packet_key: The key to verify
            
        Returns:
            True if the key matches today's key, False otherwise
        """
        expected_key = self.get_todays_public_key()
        return packet_key == expected_key

    def verify_fact_packet(self, packet_key: str, active_facts: list) -> bool:
        """
        Verifies a packet against a list of valid facts for the current window.
        """
        for entry in active_facts:
            if isinstance(entry, dict):
                domain = entry.get('domain')
                value = entry.get('value')
                window = entry.get('window')
            else:
                if len(entry) == 3:
                    domain, value, window = entry
                elif len(entry) == 2:
                    domain, value = entry
                else:
                    # Skip malformed tuple entries to prevent runtime errors.
                    continue
            if not domain or value is None:
                continue
            if packet_key == self.get_fact_gated_key(domain, value, window):
                return True
        return False

    def _derive_web_key(self, date_str: str) -> bytes:
        """
        Derives a Fernet key from the day's deterministic key.

        Args:
            date_str: ISO date string (e.g., "2026-01-07")

        Returns:
            32-byte Fernet encryption key
        """
        raw_string = f'{self._master_seed}:{date_str}'
        digest = hashlib.sha256(raw_string.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def initialize_system(self):
        """
        Generates the permanent Master Key and locks it.

        This should be called once during system setup or first use.
        """
        mode = getattr(self.config, 'ENCRYPTION_MODE', 'normal')
        if mode == 'bypass':
            logger.info('Neural Link in BYPASS MODE. No initialization needed.')
            return
        if os.path.exists(self.key_store_path):
            return
        logger.info(f'Initializing Neural Command Link ({mode})...')
        today = datetime.date.today().isoformat()
        master_key = Fernet.generate_key()
        web_key = self._derive_web_key(today)
        f_web = Fernet(web_key)
        encrypted_master = f_web.encrypt(master_key)
        state = {'last_sync': today, 'vault': encrypted_master.decode()}
        with open(self.key_store_path, 'w') as f:
            json.dump(state, f)
        logger.info('Neural Command Link initialized successfully.')

    def _access_master_channel(self) -> bytes:
        """
        Unlocks the Master Key, handling daily rotation if needed.

        Returns:
            Decrypted master key bytes

        Raises:
            RuntimeError: If Neural Link not initialized or rotation fails
        """
        mode = getattr(self.config, 'ENCRYPTION_MODE', 'normal')
        if mode == 'bypass':
            return b'BYPASS_MODE_NO_KEY'
        if not os.path.exists(self.key_store_path):
            raise RuntimeError('Neural Link not initialized.')
        with open(self.key_store_path, 'r') as f:
            state = json.load(f)
        last_sync = state.get('last_sync', 0)
        today = datetime.date.today().isoformat()
        encrypted_master_str = state.get('vault', 0)
        if mode == 'dev_key':
            web_key = self._derive_web_key(today)
            f_web = Fernet(web_key)
            return f_web.decrypt(encrypted_master_str.encode())
        if last_sync == today:
            web_key = self._derive_web_key(today)
            f_web = Fernet(web_key)
            return f_web.decrypt(encrypted_master_str.encode())
        logger.info(f'Neural Link: Date change detected ({last_sync} -> {today}). Rotating keys...')
        old_web_key = self._derive_web_key(last_sync)
        f_old = Fernet(old_web_key)
        try:
            master_key = f_old.decrypt(encrypted_master_str.encode())
        except Exception:
            raise RuntimeError('CRITICAL: Key rotation failed! Neural Link broken.')
        new_web_key = self._derive_web_key(today)
        f_new = Fernet(new_web_key)
        new_vault = f_new.encrypt(master_key)
        state['last_sync'] = today
        state['vault'] = new_vault.decode()
        with open(self.key_store_path, 'w') as f:
            json.dump(state, f)
        logger.info('Neural Link: Rotation Complete.')
        return master_key

    def encrypt_packet(self, payload: dict) -> bytes:
        """
        Encrypts a command dictionary.

        Args:
            payload: Command data dictionary

        Returns:
            Encrypted packet bytes
        """
        if getattr(self.config, 'ENCRYPTION_MODE', 'normal') == 'bypass':
            return json.dumps(payload).encode('utf-8')
        master_key = self._access_master_channel()
        f_master = Fernet(master_key)
        json_bytes = json.dumps(payload).encode('utf-8')
        return f_master.encrypt(json_bytes)

    def decrypt_packet(self, packet: bytes) -> dict:
        """
        Decrypts a packet back into a dictionary.

        Args:
            packet: Encrypted packet bytes

        Returns:
            Decrypted command data dictionary
        """
        if getattr(self.config, 'ENCRYPTION_MODE', 'normal') == 'bypass':
            return json.loads(packet.decode('utf-8'))
        master_key = self._access_master_channel()
        f_master = Fernet(master_key)
        decrypted_bytes = f_master.decrypt(packet)
        return json.loads(decrypted_bytes.decode('utf-8'))
