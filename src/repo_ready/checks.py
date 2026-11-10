"""Read-only checks for common open-source repository health signals."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


def _root_file(root: Path, *stems: str) -> bool:
    """Match README, README.md, and similar root-level naming conventions."""
    allowed = {stem.casefold() for stem in stems}
    return any(
        child.is_file() and child.stem.casefold() in allowed
        for child in root.iterdir()
    )


def _one_of(root: Path, paths: tuple[str, ...]) -> bool:
    return any((root / relative).is_file() for relative in paths)


def _named_doc(root: Path, name: str) -> bool:
    return _root_file(root, name) or ((root / ".github").is_dir() and _root_file(root / ".github", name))


def _issue_template(root: Path) -> bool:
    folder = root / ".github" / "ISSUE_TEMPLATE"
    if not folder.is_dir():
        return False
    return any(
        p.is_file() and p.name.lower() != "config.yml" and p.suffix.lower() in {".md", ".yml", ".yaml"}
        for p in folder.iterdir()
    )


def _pr_template(root: Path) -> bool:
    if _one_of(root, ("PULL_REQUEST_TEMPLATE.md", ".github/PULL_REQUEST_TEMPLATE.md", "docs/PULL_REQUEST_TEMPLATE.md")):
        return True
    folder = root / ".github" / "PULL_REQUEST_TEMPLATE"
    return folder.is_dir() and any(p.is_file() and p.suffix.lower() == ".md" for p in folder.iterdir())


def _ci(root: Path) -> bool:
    folder = root / ".github" / "workflows"
    return folder.is_dir() and any(p.is_file() and p.suffix.lower() in {".yml", ".yaml"} for p in folder.iterdir())


def _tests(root: Path) -> bool:
    patterns = ("test_*.py", "*_test.py", "*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts", "*.test.tsx", "*.spec.tsx")
    for folder in (root / "tests", root / "test", root / "spec", root / "__tests__"):
        if folder.is_dir() and any(p.is_file() for pattern in patterns for p in folder.rglob(pattern)):
            return True
    return any(p.is_file() for pattern in patterns for p in root.glob(pattern))


def _manifest(root: Path) -> bool:
    return _one_of(root, (
        "pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml",
        "go.mod", "Gemfile", "composer.json", "pom.xml", "build.gradle",
        "requirements.txt", "pubspec.yaml", "CMakeLists.txt", "Makefile",
    ))


@dataclass(frozen=True)
class Check:
    id: str
    label: str
    weight: int
    fix: str
    detector: Callable[[Path], bool]


CHECKS: tuple[Check, ...] = (
    Check("readme", "Project README", 15, "Add a README.md explaining purpose, setup, and usage.", lambda root: _root_file(root, "README")),
    Check("license", "Open-source license", 15, "Add a LICENSE file with an appropriate OSI-approved license.", lambda root: _root_file(root, "LICENSE", "LICENCE", "COPYING")),
    Check("contributing", "Contribution guide", 10, "Add CONTRIBUTING.md with development and pull-request instructions.", lambda root: _named_doc(root, "CONTRIBUTING")),
    Check("code_of_conduct", "Code of conduct", 5, "Add CODE_OF_CONDUCT.md describing community expectations.", lambda root: _named_doc(root, "CODE_OF_CONDUCT")),
    Check("security", "Security policy", 10, "Add SECURITY.md with a private vulnerability-reporting route.", lambda root: _named_doc(root, "SECURITY")),
    Check("gitignore", "Git ignore rules", 5, "Add a .gitignore that excludes build artifacts and local secrets.", lambda root: _one_of(root, (".gitignore",))),
    Check("issue_template", "Issue template", 5, "Add an issue form or Markdown template under .github/ISSUE_TEMPLATE/.", _issue_template),
    Check("pr_template", "Pull request template", 5, "Add .github/PULL_REQUEST_TEMPLATE.md.", _pr_template),
    Check("ci", "Continuous integration", 10, "Add a GitHub Actions workflow under .github/workflows/.", _ci),
    Check("tests", "Automated tests", 10, "Add test files in tests/, test/, spec/, or __tests__/.", _tests),
    Check("changelog", "Changelog", 5, "Add CHANGELOG.md to document user-facing changes.", lambda root: _root_file(root, "CHANGELOG", "HISTORY")),
    Check("manifest", "Project metadata", 5, "Add a build or package manifest such as pyproject.toml or package.json.", _manifest),
)


@dataclass(frozen=True)
class CheckResult:
    id: str
    label: str
    weight: int
    passed: bool
    fix: str


@dataclass(frozen=True)
class ScanReport:
    path: str
    score: int
    earned_points: int
    possible_points: int
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "score": self.score,
            "earned_points": self.earned_points,
            "possible_points": self.possible_points,
            "checks": [asdict(check) for check in self.checks],
        }


def scan(root: Path, ignored: set[str] | None = None) -> ScanReport:
    """Scan local filenames only; never execute project code or read file contents."""
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    ignored = ignored or set()
    allowed = {check.id for check in CHECKS}
    unknown = ignored - allowed
    if unknown:
        raise ValueError(f"Unknown check ID(s): {', '.join(sorted(unknown))}")
    selected = [check for check in CHECKS if check.id not in ignored]
    if not selected:
        raise ValueError("Cannot ignore every check")

    results = tuple(
        CheckResult(check.id, check.label, check.weight, bool(check.detector(root)), check.fix)
        for check in selected
    )
    possible = sum(result.weight for result in results)
    earned = sum(result.weight for result in results if result.passed)
    score = round(100 * earned / possible)
    return ScanReport(str(root), score, earned, possible, results)
