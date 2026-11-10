# Repo Ready

**A dependency-free CLI that checks whether your open-source repository is welcoming, maintainable, and documented.**

Starting an open-source project is easy. Maintaining one is harder. Repo Ready checks 12 common community and engineering signals, offers actionable fixes, and calculates a weighted readiness score. It works offline, does not execute your project, and never reads file contents.

> **Scope:** A checklist, not an endorsement. A high score does not prove code quality, safety, popularity, or eligibility for any developer program.

## Features

- Quick checks for README, license, contribution guide, security policy, tests, CI, issue templates and more.
- Human-readable recommendations or structured JSON for scripts.
- Exit code thresholds for CI workflows.
- Zero runtime dependencies and no network calls.
- Read-only: checks directory and file names, not file contents.

## Requirements

Python 3.10 or newer. No third-party runtime libraries.

## Install

From a downloaded copy of this repository:

```bash
python -m pip install -e .
```

## Use

```bash
# Check the current repository
repo-ready .

# Check a different local project
repo-ready ../my-project

# Return JSON to integrate with another tool
repo-ready ../my-project --format json

# Fail CI if the readiness score is under 80
repo-ready . --min-score 80

# Require every check
repo-ready . --strict

# Ignore checks that aren't relevant to a project
repo-ready . --ignore changelog,issue_template

# View supported check IDs
repo-ready --list-checks
```

You can also run the command using `python -m repo_ready .` after installation.

Example output for an empty directory:

```text
Readiness score: 0/100 (0/100 weighted points)

MISS  Project README [15 pts]
      Tip: Add a README.md explaining purpose, setup, and usage.
MISS  Open-source license [15 pts]
      Tip: Add a LICENSE file with an appropriate OSI-approved license.
...
```

The exit status is `0` when the score meets the requested minimum, `1` when below the threshold, and `2` for invalid paths or check IDs. Invalid CLI argument values also produce an error.

## Checks

| Check ID | Points | What is detected |
|---|---:|---|
| `readme` | 15 | Root README file |
| `license` | 15 | Root LICENSE, LICENCE, or COPYING |
| `contributing` | 10 | CONTRIBUTING guide (root or `.github/`) |
| `code_of_conduct` | 5 | CODE_OF_CONDUCT guide |
| `security` | 10 | SECURITY reporting guide |
| `gitignore` | 5 | `.gitignore` |
| `issue_template` | 5 | Issue template under `.github/ISSUE_TEMPLATE/` |
| `pr_template` | 5 | Pull request template |
| `ci` | 10 | GitHub Actions workflow YAML |
| `tests` | 10 | Common Python/JavaScript test filenames |
| `changelog` | 5 | CHANGELOG or HISTORY |
| `manifest` | 5 | Common language/package manifests |

Each check tests file presence or naming. It does **not** validate file content, CI effectiveness, license compatibility, or tests actually running.

The score is the percentage of available weighted points, rounded to the nearest integer. Ignored checks are removed from the denominator, so scores remain on a 0–100 scale.

## Develop

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
repo-ready . --strict
```

Tests run in CI on Python 3.10, 3.12, and 3.13.

## Contribute

Issues and pull requests are welcome. Fix a documented detection case, improve the accessibility of outputs, or add a language-specific readiness check. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ROADMAP.md](docs/ROADMAP.md) before proposing changes.

## Security and privacy

The tool is offline and reads filenames only. It neither reads secrets nor uploads repository information. Please report security issues privately according to [SECURITY.md](SECURITY.md).

## License

MIT; see [LICENSE](LICENSE).
