#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

SCENARIOS = {
    "browser_crash_recovery": "tests/lifecycle/test_browser_crash_recovery.py",
    "context_closure_recovery": "tests/lifecycle/test_context_closure_recovery.py",
    "page_detach_recovery": "tests/lifecycle/test_page_detach_recovery.py",
    "stale_selector_recovery": "tests/lifecycle/test_stale_selector_recovery.py",
    "parallel_session_isolation": "tests/lifecycle/test_parallel_session_isolation.py",
}


@dataclass
class ScenarioResult:
    name: str
    nodeid: str
    ok: bool
    return_code: int
    duration_ms: int
    stdout_tail: str
    stderr_tail: str


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic browser lifecycle fault harness")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS.keys()),
        help="Run only selected scenario(s). Can be passed multiple times.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for lifecycle-fault-results.json and lifecycle-fault-summary.md",
    )
    return parser.parse_args()


def _tail(text: str, lines: int = 25) -> str:
    split = text.strip().splitlines()
    if not split:
        return ""
    return "\n".join(split[-lines:])


def _run_one(name: str, nodeid: str) -> ScenarioResult:
    started = perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", nodeid],
        capture_output=True,
        text=True,
        check=False,
    )
    duration_ms = int((perf_counter() - started) * 1000)
    return ScenarioResult(
        name=name,
        nodeid=nodeid,
        ok=proc.returncode == 0,
        return_code=proc.returncode,
        duration_ms=duration_ms,
        stdout_tail=_tail(proc.stdout),
        stderr_tail=_tail(proc.stderr),
    )


def _write_summary(path: Path, *, started_at: str, results: list[ScenarioResult]) -> None:
    passed = sum(1 for r in results if r.ok)
    failed = len(results) - passed
    lines = [
        "# Lifecycle Fault Harness Summary",
        "",
        f"- started_at: {started_at}",
        f"- total: {len(results)}",
        f"- passed: {passed}",
        f"- failed: {failed}",
        "",
        "## Scenario Results",
        "",
    ]
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        lines.append(
            f"- `{result.name}`: {status} ({result.duration_ms} ms) [{result.nodeid}]"
        )
    lines.append("")
    lines.append("## Failure Tails")
    lines.append("")
    any_failures = False
    for result in results:
        if result.ok:
            continue
        any_failures = True
        lines.append(f"### {result.name}")
        lines.append("")
        lines.append("```text")
        lines.append(result.stdout_tail or "<no stdout>")
        if result.stderr_tail:
            lines.append("--- stderr ---")
            lines.append(result.stderr_tail)
        lines.append("```")
        lines.append("")
    if not any_failures:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = _parse_args()
    selected = args.scenario or list(SCENARIOS.keys())

    started_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path("docs/harness/browser-lifecycle-fault-injection") / started_at
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    results = [_run_one(name, SCENARIOS[name]) for name in selected]
    passed = sum(1 for r in results if r.ok)
    failed = len(results) - passed

    payload = {
        "started_at": started_at,
        "output_dir": str(output_dir),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": [asdict(r) for r in results],
    }

    results_path = output_dir / "lifecycle-fault-results.json"
    summary_path = output_dir / "lifecycle-fault-summary.md"

    results_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_summary(summary_path, started_at=started_at, results=results)

    print(f"wrote {results_path}")
    print(f"wrote {summary_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
