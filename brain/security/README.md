# 🔒 Security - Encryption & Access Control

**Security components for the Brain system.**

---

## Overview

The `brain/security/` directory contains security-related components including encryption, secure channels, and AI policy enforcement.

---

## Components

| File | Purpose |
|------|---------|
| `crypto_engine.py` | Encryption and decryption |
| `neural_link.py` | Secure command channel |
| `export_guard.py` | Data export protection |
| `ai_policy_enforcer.py` | AI operation policies |

---

## Crypto Engine

Encryption and decryption for sensitive data:

```python
from brain.security.crypto_engine import CryptoEngine

crypto = CryptoEngine()

# Encrypt data
encrypted = crypto.encrypt("sensitive data")

# Decrypt data
decrypted = crypto.decrypt(encrypted)

# Generate key
key = crypto.generate_key()
```

---

## Neural Link

Secure command channel with daily rotating keys:

```python
from brain.security.neural_link import NeuralCommandLink

link = NeuralCommandLink()

# Initialize
link.initialize_system()

# Create encrypted packet
packet = link.create_packet(command_data)

# Decrypt packet
data = link.decrypt_packet(packet)
```

---

## Export Guard

Protects sensitive data during export:

```python
from brain.security.export_guard import ExportGuard

guard = ExportGuard()

# Check if export is allowed
result = guard.check_export(
    user_id="user123",
    data_type="customers"
)

# Sanitize export data
sanitized = guard.sanitize(data)
```

---

## AI Policy Enforcer

Enforces policies for AI operations:

```python
from brain.security.ai_policy_enforcer import AIPolicyEnforcer

enforcer = AIPolicyEnforcer()

# Check AI operation
result = enforcer.check_operation(
    operation="code_generation",
    context={"file": "brain/core/brain.py"}
)
```

---

## Cross-References

| Topic | File |
|-------|------|
| Security policy | `brain/policies/security.py` |
| Privacy | `brain/privacy/README.md` |
| Core brain | `brain/core/README.md` |

---

**Last Updated:** February 2026