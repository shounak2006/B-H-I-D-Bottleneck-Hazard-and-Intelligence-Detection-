"""
Unit tests for BHID Documentation Completeness (Phase 6B).

Validates:
1. Existence of all required root-level Markdown guides
2. Presence of major section headers without enforcing exact wording
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))


class TestDocumentationCompleteness(unittest.TestCase):

    def setUp(self):
        self.project_root = PROJECT_ROOT
        self.required_docs = {
            "INSTALLATION.md": ["Prerequisites", "Installation Steps"],
            "OPERATOR_GUIDE.md": ["System Overview", "Monitoring Workflow"],
            "ARCHITECTURE_GUIDE.md": ["Architecture", "Package Responsibilities"],
            "DEVELOPER_GUIDE.md": ["Repository", "Coding Standards"],
            "MAINTENANCE_GUIDE.md": ["Updating Dependencies", "Maintenance"],
            "OPERATIONS_RUNBOOK.md": ["initialize_bhid", "shutdown_bhid"],
            "TESTING_GUIDE.md": ["Testing", "Smoke Testing"],
            "RELEASE_NOTES_v1.0.md": ["Release", "Roadmap"],
            "SYSTEM_CAPABILITIES.md": ["Capabilities", "Inventory"],
            "HANDOVER_PACKAGE.md": ["Handover", "Architecture Summary"]
        }

    def test_required_documentation_files_exist(self):
        """Verifies that all required root-level Markdown documents exist."""
        for doc_name in self.required_docs.keys():
            doc_path = self.project_root / doc_name
            self.assertTrue(doc_path.exists(), f"Required documentation file missing: {doc_name}")

    def test_major_section_headers_exist(self):
        """Verifies presence of major section headers non-brittly."""
        for doc_name, keywords in self.required_docs.items():
            doc_path = self.project_root / doc_name
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()

            for kw in keywords:
                self.assertIn(kw.lower(), content.lower(), f"Keyword '{kw}' missing from {doc_name}")


if __name__ == "__main__":
    unittest.main()
