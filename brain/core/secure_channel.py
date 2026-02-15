"""
Secure Channel for Inter-Brain Communication

This module provides cryptographic envelopes for Zero Trust inter-brain messaging:
- Ed25519 digital signatures for authentication and non-repudiation
- X25519 key exchange + Salsa20-Poly1305 AEAD for confidentiality and integrity
- Envelope pattern with signed headers, encrypted payloads, nonces, and key IDs
- Protection against spoofing, tampering, and replay attacks

Note: PyNaCl's Box uses X25519 + Salsa20-Poly1305, not ChaCha20-Poly1305.

Architecture:
1. Each brain has an Ed25519 signing keypair (long-lived)
2. Each brain has an X25519 encryption keypair (rotatable)
3. Messages are signed with sender's signing key
4. Messages are encrypted with recipient's public key using Box (X25519 + Salsa20-Poly1305)
5. Envelope includes: signed_header + encrypted_payload + timestamp + nonce + kid

Usage:
    from brain.core.secure_channel import create_envelope, verify_envelope
    
    # Sender creates envelope
    envelope = create_envelope(
        sender_signing_key=sender_signing_privkey,
        recipient_public_key=recipient_pubkey,
        payload={"command": "create_customer", "params": {...}},
        sender_kid="ops-brain-2024-01",
        recipient_kid="finance-brain-2024-01"
    )
    
    # Recipient verifies and decrypts
    payload = verify_envelope(
        envelope=envelope,
        recipient_private_key=recipient_privkey,
        sender_public_key=sender_pubkey,
        nonce_ledger=nonce_ledger
    )

Part of: Secure Channel Cryptographic Messaging (Phase 1 PoC)
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import os
import json
import time
import base64
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import nacl.secret
import nacl.utils
import nacl.signing
import nacl.encoding
import nacl.public
import nacl.exceptions
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey, Box
from brain.core import nonce_ledger
logger = logging.getLogger(__name__)

class SecureChannelError(Exception):
    """Base exception for secure channel errors"""
    pass

class EnvelopeFormatError(SecureChannelError):
    """Raised when envelope format is invalid"""
    pass

class SignatureVerificationError(SecureChannelError):
    """Raised when signature verification fails"""
    pass

class DecryptionError(SecureChannelError):
    """Raised when decryption fails"""
    pass

class ReplayAttackError(SecureChannelError):
    """Raised when a message is replayed (nonce reuse detected)"""
    pass

class TimestampError(SecureChannelError):
    """Raised when message timestamp is outside acceptable window"""
    pass
TIMESTAMP_TOLERANCE_SECONDS = 300
NONCE_LENGTH = 24

def generate_signing_keypair() -> Tuple[bytes, bytes]:
    """
    Generate a new Ed25519 signing keypair.
    
    Returns:
        (private_key, public_key): Both as 32-byte values
    """
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    return (signing_key.encode(), verify_key.encode())

def generate_encryption_keypair() -> Tuple[bytes, bytes]:
    """
    Generate a new X25519 encryption keypair.
    
    Returns:
        (private_key, public_key): Both as 32-byte values
    """
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    return (bytes(private_key), bytes(public_key))

def create_envelope(sender_signing_key: bytes, recipient_public_key: bytes, payload: Dict[str, Any], sender_kid: str, recipient_kid: str, sender_private_encryption_key: Optional[bytes]=None, metadata: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    """
    Create a signed and encrypted envelope for inter-brain communication.
    
    The envelope structure is:
    {
        "version": "1.0",
        "sender_kid": "ops-brain-2024-01",
        "recipient_kid": "finance-brain-2024-01",
        "timestamp": 1704934800.123,
        "nonce": "base64-encoded-24-bytes",
        "signed_header": "base64-encoded-signature",
        "encrypted_payload": "base64-encoded-ciphertext",
        "fact_context": {...},  # optional (signed header field when provided)
        "metadata": {...}  # optional
    }
    
    Args:
        sender_signing_key: Sender's Ed25519 private signing key (32 bytes)
        recipient_public_key: Recipient's X25519 public encryption key (32 bytes)
        payload: Dictionary to encrypt (will be JSON-serialized)
        sender_kid: Sender's key ID (for key rotation)
        recipient_kid: Recipient's key ID
        sender_private_encryption_key: Sender's X25519 private key (32 bytes)
                                       If None, generates ephemeral keypair
        metadata: Optional metadata (not encrypted, but signed). Must include audit_log_id.
        
    Returns:
        Envelope dictionary ready for transmission
        
    Raises:
        SecureChannelError: If envelope creation fails
    """
    try:
        timestamp = time.time()
        nonce = nacl.utils.random(NONCE_LENGTH)
        payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        payload_bytes = payload_json.encode('utf-8')
        payload_hash = hashlib.sha256(payload_bytes).digest()
        header = {'version': '1.0', 'sender_kid': sender_kid, 'recipient_kid': recipient_kid, 'timestamp': timestamp, 'nonce': base64.b64encode(nonce).decode('ascii'), 'payload_hash': base64.b64encode(payload_hash).decode('ascii')}
        fact_context = metadata.get('fact_context') if metadata else None
        if fact_context:
            header['fact_context'] = fact_context
        if metadata:
            header['metadata'] = metadata
        header_json = json.dumps(header, separators=(',', ':'), sort_keys=True)
        header_bytes = header_json.encode('utf-8')
        signing_key = SigningKey(sender_signing_key)
        signed_message = signing_key.sign(header_bytes)
        signature = signed_message.signature
        if sender_private_encryption_key is None:
            sender_private_encryption_key = bytes(PrivateKey.generate())
        sender_private = PrivateKey(sender_private_encryption_key)
        recipient_public = PublicKey(recipient_public_key)
        box = Box(sender_private, recipient_public)
        encrypted_payload = box.encrypt(payload_bytes, nonce)
        ciphertext = encrypted_payload[NONCE_LENGTH:]
        envelope = {'version': '1.0', 'sender_kid': sender_kid, 'recipient_kid': recipient_kid, 'timestamp': timestamp, 'nonce': base64.b64encode(nonce).decode('ascii'), 'signed_header': base64.b64encode(signature).decode('ascii'), 'encrypted_payload': base64.b64encode(ciphertext).decode('ascii')}
        if metadata:
            envelope['metadata'] = metadata
        logger.info(f'Created secure envelope: {sender_kid} -> {recipient_kid}')
        return envelope
    except Exception as e:
        logger.error(f'Failed to create envelope: {e}')
        raise SecureChannelError(f'Envelope creation failed: {e}')

def verify_envelope(envelope: Dict[str, Any], recipient_private_key: bytes, sender_public_key: bytes, sender_public_signing_key: bytes, nonce_ledger: Optional['NonceLedger'] = None, timestamp_tolerance: int = TIMESTAMP_TOLERANCE_SECONDS) -> Dict[str, Any]:
    """
    Verify and decrypt a secure envelope.
    
    This function performs the following checks:
    1. Envelope format validation
    2. Timestamp validation (prevent stale messages)
    3. Signature verification (authenticate sender)
    4. Nonce replay check (prevent replay attacks)
    5. Decryption (restore plaintext payload)
    6. Payload hash verification (detect tampering)
    
    Args:
        envelope: Envelope dictionary to verify
        recipient_private_key: Recipient's X25519 private encryption key (32 bytes)
        sender_public_key: Sender's X25519 public encryption key (32 bytes)
        sender_public_signing_key: Sender's Ed25519 public signing key (32 bytes)
        nonce_ledger: Optional nonce tracking service for replay protection
        timestamp_tolerance: Maximum age of message in seconds (default: 300)
        
    Returns:
        Decrypted payload dictionary
        
    Raises:
        EnvelopeFormatError: If envelope structure is invalid
        SignatureVerificationError: If signature check fails
        TimestampError: If message is too old or from future
        ReplayAttackError: If nonce has been seen before
        DecryptionError: If decryption fails
    """
    try:
        required_fields = ['version', 'sender_kid', 'recipient_kid', 'timestamp', 'nonce', 'signed_header', 'encrypted_payload']
        for field in required_fields:
            if field not in envelope:
                raise EnvelopeFormatError(f'Missing required field: {field}')
        if envelope.get('version', 0) != '1.0':
            raise EnvelopeFormatError(f"Unsupported envelope version: {envelope.get('version', 0)}")
        sender_kid = envelope.get('sender_kid', 0)
        recipient_kid = envelope.get('recipient_kid', 0)
        timestamp = envelope.get('timestamp', 0)
        nonce_b64 = envelope.get('nonce', 0)
        signature_b64 = envelope.get('signed_header', 0)
        ciphertext_b64 = envelope.get('encrypted_payload', 0)
        metadata = envelope.get('metadata')
        audit_log_id = None
        if metadata:
            audit_log_id = metadata.get('audit_log_id')
        if not audit_log_id:
            raise EnvelopeFormatError('Missing audit_log_id in envelope metadata')
        nonce = base64.b64decode(nonce_b64)
        signature = base64.b64decode(signature_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        current_time = time.time()
        age = current_time - timestamp
        if age < -30:
            raise TimestampError(f'Message from future: {-age:.1f}s ahead')
        if age > timestamp_tolerance:
            raise TimestampError(f'Message too old: {age:.1f}s (max: {timestamp_tolerance}s)')
        # Check for replay attacks before decryption
        if nonce_ledger:
            if nonce_ledger.check_nonce(sender_kid, nonce_b64):
                raise ReplayAttackError(f'Nonce reuse detected from {sender_kid}')

        # Decrypt payload first (needed to compute payload hash for signature verification)
        recipient_private = PrivateKey(recipient_private_key)
        sender_public = PublicKey(sender_public_key)
        box = Box(recipient_private, sender_public)
        encrypted_message = nonce + ciphertext
        try:
            decrypted_bytes = box.decrypt(encrypted_message)
        except Exception as e:
            raise DecryptionError(f'Decryption failed: {e}')
        try:
            payload = json.loads(decrypted_bytes.decode('utf-8'))
        except Exception as e:
            raise DecryptionError(f'Payload deserialization failed: {e}')

        # Now verify the signature against the reconstructed header (including payload hash)
        verify_key = VerifyKey(sender_public_signing_key)

        # Compute payload hash for signature verification
        payload_hash = hashlib.sha256(decrypted_bytes).digest()

        # Reconstruct the header exactly as it was signed in create_envelope
        header = {
            'version': '1.0',
            'sender_kid': sender_kid,
            'recipient_kid': recipient_kid,
            'timestamp': timestamp,
            'nonce': nonce_b64,
            'payload_hash': base64.b64encode(payload_hash).decode('ascii')
        }
        # Include fact_context and metadata if present (they were included in signing)
        if metadata:
            fact_context = metadata.get('fact_context')
            if fact_context:
                header['fact_context'] = fact_context
            header['metadata'] = metadata

        header_json = json.dumps(header, separators=(',', ':'), sort_keys=True)
        header_bytes = header_json.encode('utf-8')

        try:
            # Verify the signature against the reconstructed header
            verify_key.verify(header_bytes, signature)
            logger.debug('Signature verification successful')
        except nacl.exceptions.BadSignature:
            raise SignatureVerificationError('Signature verification failed - message may be tampered or from wrong sender')
        if nonce_ledger:
            nonce_ledger.record_nonce(
                sender_kid,
                nonce_b64,
                timestamp_tolerance,
                metadata={'audit_log_id': audit_log_id},
            )
        logger.info(f'Successfully verified envelope: {sender_kid} -> {recipient_kid}')
        return payload
    except SecureChannelError:
        raise
    except Exception as e:
        logger.error(f'Envelope verification failed: {e}')
        raise SecureChannelError(f'Envelope verification failed: {e}')

def key_to_base64(key: bytes) -> str:
    """Convert a key to base64 for storage"""
    return base64.b64encode(key).decode('ascii')

def key_from_base64(key_b64: str) -> bytes:
    """Convert a base64 key back to bytes"""
    return base64.b64decode(key_b64)

def generate_kid(brain_name: str, key_type: str) -> str:
    """
    Generate a key ID (kid) for key rotation.
    
    Args:
        brain_name: Name of the brain (e.g., "ops", "finance", "relation")
        key_type: Type of key (e.g., "signing", "encryption")
        
    Returns:
        Key ID string (e.g., "ops-signing-2024-01-08")
    """
    from datetime import datetime, timezone
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    return f'{brain_name}-{key_type}-{date_str}'
