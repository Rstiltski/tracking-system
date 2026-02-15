"""
Brain Security Module

Phase 9.2: Export Guard and other security features
📚 REQUIRED READING BEFORE MODIFICATION:
- SECURITY_GUIDE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from .export_guard import ExportGuard, check_export_allowed, add_export_watermark

__all__ = ['ExportGuard', 'check_export_allowed', 'add_export_watermark']

