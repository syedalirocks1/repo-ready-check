"""Coverage for repository detection and weighting."""

import tempfile
import unittest
from pathlib import Path

from repo_ready.checks import CHECKS, scan


class TestChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def create(self, filename, text="sample\n"):
        target = self.root / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def as_map(self):
        return {check.id: check.passed for check in scan(self.root).checks}

    def test_empty_repo_scores_zero(self):
        report = scan(self.root)
        self.assertEqual(0, report.score)
        self.assertEqual(100, report.possible_points)
        self.assertEqual(12, len(report.checks))

    def test_readme_names_case_insensitive(self):
        self.create("ReadMe.rst")
        self.assertTrue(self.as_map()["readme"])

    def test_license_copies(self):
        self.create("COPYING")
        self.assertTrue(self.as_map()["license"])

    def test_nested_guides(self):
        self.create(".github/CONTRIBUTING.md")
        self.create(".github/SECURITY.md")
        self.create(".github/CODE_OF_CONDUCT.md")
        flags = self.as_map()
        self.assertTrue(flags["contributing"])
        self.assertTrue(flags["security"])
        self.assertTrue(flags["code_of_conduct"])

    def test_issue_config_not_counted(self):
        self.create(".github/ISSUE_TEMPLATE/config.yml")
        self.assertFalse(self.as_map()["issue_template"])
        self.create(".github/ISSUE_TEMPLATE/bug.yml")
        self.assertTrue(self.as_map()["issue_template"])

    def test_pr_and_ci(self):
        self.create(".github/PULL_REQUEST_TEMPLATE.md")
        self.create(".github/workflows/build.yaml")
        flags = self.as_map()
        self.assertTrue(flags["pr_template"])
        self.assertTrue(flags["ci"])

    def test_nested_pr_template(self):
        self.create(".github/PULL_REQUEST_TEMPLATE/feature.md")
        self.assertTrue(self.as_map()["pr_template"])

    def test_python_tests_detected(self):
        self.create("tests/test_example.py")
        self.assertTrue(self.as_map()["tests"])

    def test_js_tests_detected(self):
        self.create("__tests__/core.test.js")
        self.assertTrue(self.as_map()["tests"])

    def test_project_metadata_detected(self):
        self.create("package.json")
        self.assertTrue(self.as_map()["manifest"])

    def test_ignore_scales_score(self):
        self.create("README.md")
        result = scan(self.root, {"license", "ci"})
        self.assertEqual(75, result.possible_points)
        self.assertEqual(20, result.score)
        self.assertEqual(10, len(result.checks))

    def test_unknown_ignore_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown check"):
            scan(self.root, {"nonsense"})

    def test_all_ignored_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "every check"):
            scan(self.root, {check.id for check in CHECKS})

    def test_invalid_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Not a directory"):
            scan(self.root / "not-here")

    def test_json_payload_is_structured(self):
        self.create("README.md")
        report = scan(self.root).to_dict()
        self.assertEqual(15, report["earned_points"])
        self.assertEqual("readme", report["checks"][0]["id"])
        self.assertTrue(report["checks"][0]["passed"])


if __name__ == "__main__":
    unittest.main()
