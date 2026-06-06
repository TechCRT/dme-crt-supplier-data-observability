from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GitHubReadinessAssetTests(unittest.TestCase):
    def test_required_phase4_files_exist(self) -> None:
        required_paths = [
            ROOT / "README.md",
            ROOT / "LICENSE",
            ROOT / ".gitignore",
            ROOT / "docs" / "data_dictionary.md",
            ROOT / "docs" / "validation_rules.md",
            ROOT / "docs" / "operating_notes.md",
            ROOT / "docs" / "proof_notes.md",
            ROOT / "docs" / "github_release_checklist.md",
            ROOT / ".github" / "workflows" / "python-tests.yml",
        ]

        for path in required_paths:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"Missing required Phase 4 asset: {path}")

    def test_readme_preserves_public_safe_claim_boundaries(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.assertIn("public-safe", readme)
        self.assertIn("no pbix file or real dashboard screenshots", readme)
        self.assertIn("does not provide billing guidance", readme)
        self.assertIn("future re-entry warnings", readme)

    def test_claim_boundary_docs_reject_disallowed_claims(self) -> None:
        docs = "\n".join(
            [
                (ROOT / "docs" / "operating_notes.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "github_release_checklist.md").read_text(encoding="utf-8"),
            ]
        ).lower()

        required_boundary_phrases = [
            "production deployment",
            "billing automation",
            "payer policy logic",
            "clinical decisioning",
            "private-data processing",
            "pbix completion",
            "real screenshots",
        ]
        for phrase in required_boundary_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, docs)

    def test_github_workflow_runs_unittest_with_src_pythonpath(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "python-tests.yml").read_text(encoding="utf-8")

        self.assertIn("PYTHONPATH: src", workflow)
        self.assertIn("python -m unittest discover -s tests", workflow)


if __name__ == "__main__":
    unittest.main()
