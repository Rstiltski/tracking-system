"""
DocsBrain - The Librarian

Responsibilities:
- Keep documentation in sync with code
- Update BRAIN.md when architecture changes
- Track what documentation exists
- Suggest documentation updates

This brain ensures the MD files stay accurate.
"""
import os
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from brain.nervous_system import NervousSystem, get_nervous_system


@dataclass
class DocInfo:
    """Information about a documentation file"""
    path: str
    name: str
    size_bytes: int
    line_count: int
    last_modified: str
    doc_type: str  # 'brain', 'reference', 'guide', 'archive'


@dataclass
class DocsSyncReport:
    """Report on documentation sync status"""
    total_docs: int
    root_docs: int
    archive_docs: int
    brain_design_docs: int
    out_of_sync: List[str]
    recommendations: List[str]


class DocsBrain:
    """
    Meta-Brain: Manages documentation

    Responsibilities:
    1. Track all MD files
    2. Detect out-of-sync documentation
    3. Suggest updates when code changes
    4. Maintain BRAIN.md as single source of truth

    Workflow:
    1. Scan for all MD files
    2. Check timestamps vs code changes
    3. Identify outdated docs
    4. Emit DOCS_OUTDATED event if needed
    """

    # Key documentation files
    CRITICAL_DOCS = [
        'BRAIN.md',
        'README.md',
        'ARCHITECTURE_RULES.md',
        'TESTING_GUIDE.md',
        'TROUBLESHOOTING_GUIDE.md'
    ]

    # Documentation that should be kept in sync
    SYNC_PAIRS = {
        'brain/brains/': 'BRAIN.md',  # New brains should be documented in BRAIN.md
        'brain/core/contracts.py': 'BRAIN.md',  # EventTypes should be documented
        'database/queries/': 'DATABASE_API_REFERENCE.md',  # DB functions
        'brain/tools/': 'BRAIN_TOOLS_REFERENCE.md'  # Brain tools
    }

    def __init__(self, nervous_system: Optional[NervousSystem] = None,
                 base_path: str = "/home/user/landscaping"):
        self.nervous_system = nervous_system or get_nervous_system()
        self.base_path = base_path
        self._register_listeners()

    def _register_listeners(self):
        """Register for events from other brains"""
        pass

    def scan_docs(self) -> List[DocInfo]:
        """Scan all documentation files"""
        docs = []

        for root, dirs, files in os.walk(self.base_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.base_path)

                    # Determine doc type
                    if 'archive' in rel_path:
                        doc_type = 'archive'
                    elif 'brain/design' in rel_path:
                        doc_type = 'brain_design'
                    elif rel_path.count('/') == 0:
                        doc_type = 'root'
                    else:
                        doc_type = 'other'

                    try:
                        stat = os.stat(full_path)
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            line_count = sum(1 for _ in f)

                        docs.append(DocInfo(
                            path=rel_path,
                            name=file,
                            size_bytes=stat.st_size,
                            line_count=line_count,
                            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            doc_type=doc_type
                        ))
                    except Exception:
                        continue

        return docs

    def check_sync_status(self) -> DocsSyncReport:
        """Check if documentation is in sync with code"""
        docs = self.scan_docs()

        # Count by type
        root_docs = sum(1 for d in docs if d.doc_type == 'root')
        archive_docs = sum(1 for d in docs if d.doc_type == 'archive')
        brain_design_docs = sum(1 for d in docs if d.doc_type == 'brain_design')

        out_of_sync = []
        recommendations = []

        # Check if critical docs exist
        for doc in self.CRITICAL_DOCS:
            if not any(d.path == doc for d in docs):
                out_of_sync.append(f"Missing critical doc: {doc}")

        # Check brain count matches documentation
        brain_files = self._count_brains()
        if brain_files > 3:  # We document 3 domain brains + 6 meta brains
            recommendations.append(f"Found {brain_files} brain files - ensure all are documented in BRAIN.md")

        # Check if BRAIN.md mentions all brains
        brain_md_path = os.path.join(self.base_path, 'BRAIN.md')
        if os.path.exists(brain_md_path):
            with open(brain_md_path, 'r') as f:
                brain_md_content = f.read()

            # Check for meta brains
            meta_brains = ['ScannerBrain', 'DiagnosisBrain', 'RepairBrain',
                          'TestBrain', 'ValidatorBrain', 'DocsBrain']
            for brain in meta_brains:
                if brain not in brain_md_content:
                    out_of_sync.append(f"BRAIN.md missing documentation for {brain}")

        return DocsSyncReport(
            total_docs=len(docs),
            root_docs=root_docs,
            archive_docs=archive_docs,
            brain_design_docs=brain_design_docs,
            out_of_sync=out_of_sync,
            recommendations=recommendations
        )

    def _count_brains(self) -> int:
        """Count brain files"""
        brains_path = os.path.join(self.base_path, 'brain', 'brains')
        if not os.path.exists(brains_path):
            return 0

        count = 0
        for file in os.listdir(brains_path):
            if file.endswith('_brain.py'):
                count += 1
        return count

    def get_brain_list(self) -> List[str]:
        """Get list of all brain files"""
        brains_path = os.path.join(self.base_path, 'brain', 'brains')
        if not os.path.exists(brains_path):
            return []

        brains = []
        for file in os.listdir(brains_path):
            if file.endswith('_brain.py'):
                brains.append(file.replace('.py', ''))
        return brains

    def suggest_brain_md_update(self) -> str:
        """Generate suggested update for BRAIN.md"""
        brains = self.get_brain_list()

        domain_brains = ['ops_brain', 'finance_brain', 'relation_brain']
        meta_brains = [b for b in brains if b not in domain_brains and b != '__init__']

        suggestion = """
## Suggested BRAIN.md Update

### All Brains (Total: {total})

#### Domain Brains ({domain_count})
{domain_list}

#### Meta Brains ({meta_count})
{meta_list}
""".format(
            total=len(brains),
            domain_count=len(domain_brains),
            domain_list='\n'.join(f"- {b}" for b in domain_brains if b in brains),
            meta_count=len(meta_brains),
            meta_list='\n'.join(f"- {b}" for b in meta_brains)
        )

        return suggestion

    def get_summary(self) -> str:
        """Get documentation summary"""
        report = self.check_sync_status()

        summary = f"""
## Documentation Status

**Total MD Files:** {report.total_docs}
- Root level: {report.root_docs}
- Brain design: {report.brain_design_docs}
- Archived: {report.archive_docs}

"""
        if report.out_of_sync:
            summary += "**Out of Sync:**\n"
            for item in report.out_of_sync:
                summary += f"- {item}\n"

        if report.recommendations:
            summary += "\n**Recommendations:**\n"
            for rec in report.recommendations:
                summary += f"- {rec}\n"

        if not report.out_of_sync and not report.recommendations:
            summary += "**Status:** All documentation appears to be in sync.\n"

        return summary


# Convenience functions
def check_docs() -> DocsSyncReport:
    """Quick documentation check"""
    brain = DocsBrain()
    return brain.check_sync_status()


def list_all_brains() -> List[str]:
    """List all brain files"""
    brain = DocsBrain()
    return brain.get_brain_list()
