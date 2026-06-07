from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PowerShellAssetTests(unittest.TestCase):
    def test_required_phase2_files_exist(self) -> None:
        required_paths = [
            ROOT / "automation" / "powershell" / "Watch-IntakeFolder.ps1",
            ROOT / "automation" / "powershell" / "Run-SamplePipeline.ps1",
            ROOT / "docs" / "powershell_intake_workflow.md",
        ]

        for path in required_paths:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"Missing required Phase 2 asset: {path}")

    def test_watcher_uses_workspace_relative_routing_and_python_cli(self) -> None:
        watcher = (ROOT / "automation" / "powershell" / "Watch-IntakeFolder.ps1").read_text(encoding="utf-8")

        self.assertIn('Join-Path $rootPath "data\\intake"', watcher)
        self.assertIn('Join-Path $rootPath "data\\processing"', watcher)
        self.assertIn('Join-Path $rootPath "data\\processed"', watcher)
        self.assertIn('Join-Path $rootPath "data\\review"', watcher)
        self.assertIn('Join-Path $rootPath "data\\rejected"', watcher)
        self.assertIn("dme_crt_supplier_observability.cli", watcher)
        self.assertIn("validate-file", watcher)
        self.assertNotIn("Remove-Item", watcher)
        self.assertNotIn("D:\\", watcher)

    def test_documentation_preserves_public_safe_boundary(self) -> None:
        docs = (ROOT / "docs" / "powershell_intake_workflow.md").read_text(encoding="utf-8")

        self.assertIn("public-safe", docs.lower())
        self.assertIn("classification-support examples only", docs)
        self.assertIn("Operating Notes", docs)


if __name__ == "__main__":
    unittest.main()
