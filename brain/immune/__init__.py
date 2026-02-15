"""
Immune system modules for autonomous repair workflows.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.immune.fingerprinter import CrashReport, SemanticFingerprinter
from brain.immune.worker import ImmuneSystemWorker, ResourceLimits

__all__ = [
    "CrashReport",
    "SemanticFingerprinter",
    "ImmuneSystemWorker",
    "ResourceLimits",
]
