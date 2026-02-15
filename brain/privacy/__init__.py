"""
Brain Privacy Module - Phase 7: The Blood-Brain Barrier

This module implements PII tokenization and secure vault functionality
to prevent sensitive data from being sent to external AI providers.

Key Components:
- Tokenizer: Replaces PII with tokens before AI interaction
- Vault: Secure storage and retrieval of tokenized data
- Detokenizer: Reconstructs original data after AI response
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from .tokenizer import PIITokenizer, TokenType
from .vault import PIIVault

__all__ = ['PIITokenizer', 'TokenType', 'PIIVault']
