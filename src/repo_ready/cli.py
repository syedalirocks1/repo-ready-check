"""CLI for checking open-source project hygiene without dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .checks import CHECKS, ScanReport, scan


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo-ready",
        description="Audit common open-source repository files and practices (offline, read-only).",
    )
    parser.add_argument("path", nargs="?", default=".", help="Local repository directory (default: current directory)")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    parser.add_argument("--min-score", type=int, default=0, metavar="0-100", help="Exit 1 if score is below this value")
    parser.add_argument("--strict", action="store_true", help="Require all enabled checks to pass (same as --min-score 100)")
    parser.add_argument("--ignore", default="", metavar="IDS", help="Comma-separated check IDs to exclude")
    parser.add_argument("--list-checks", action="store_true", help="List supported check IDs and exit")
    parser.add_argument("--version", action="version", version=f"repo-ready {__version__}")
    return parser


def render_text(report: ScanReport) -> str:
    output = [f"Repository: {report.path}", f"Readiness score: {report.score}/100 ({report.earned_points}/{report.possible_points} weighted points)", ""]
    for check in report.checks:
        output.append(f"{'PASS' if check.passed else 'MISS'}  {check.label} [{check.weight} pts]")
        if not check.passed:
            output.append(f"      Tip: {check.fix}")
    output.extend(("", "Note: this score assesses files and conventions, not code quality or community impact."))
    return "\n".join(output)


def main(argv: Sequence[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    if args.list_checks:
        for check in CHECKS:
            print(f"{check.id:<17} {check.weight:>2} pts  {check.label}")
        return 0
    if not 0 <= args.min_score <= 100:
        parser.error("--min-score must be between 0 and 100")
    ignored = {item.strip() for item in args.ignore.split(",") if item.strip()}
    try:
        report = scan(Path(args.path), ignored=ignored)
    except (ValueError, OSError) as exc:
        print(f"repo-ready: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_text(report))
    return 0 if report.score >= (100 if args.strict else args.min_score) else 1
