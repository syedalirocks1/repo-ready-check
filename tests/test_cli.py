"""CLI contract: exit statuses, readable and machine-readable output."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from repo_ready.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)

    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = main([str(self.repo), *args])
        return status, out.getvalue(), err.getvalue()

    def test_text_score(self):
        status, text, err = self.call()
        self.assertEqual(0, status)
        self.assertIn("Readiness score: 0/100", text)
        self.assertEqual("", err)

    def test_threshold_failure(self):
        status, text, _ = self.call("--min-score", "70")
        self.assertEqual(1, status)
        self.assertIn("MISS", text)

    def test_strict_failure(self):
        status, _, _ = self.call("--strict")
        self.assertEqual(1, status)

    def test_json_output(self):
        status, stdout, stderr = self.call("--format", "json")
        self.assertEqual(0, status)
        payload = json.loads(stdout)
        self.assertEqual(100, payload["possible_points"])
        self.assertEqual(12, len(payload["checks"]))
        self.assertEqual("", stderr)

    def test_ignore_some_checks(self):
        status, text, _ = self.call("--ignore", "readme,license")
        self.assertEqual(0, status)
        self.assertIn("0/70 weighted points", text)

    def test_unknown_ignore_error(self):
        status, _, err = self.call("--ignore", "not_a_check")
        self.assertEqual(2, status)
        self.assertIn("Unknown check", err)

    def test_missing_path_error(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main([str(self.repo / "missing")])
        self.assertEqual(2, status)
        self.assertIn("Not a directory", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
