#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run closed-loop validation -> prioritization -> remediation cycle artifacts"
    )
    parser.add_argument("--validation-dir", default="docs/validation/telecom-browser-mcp-v0.2")
    parser.add_argument(
        "--validation-diagnostics-dir",
        default="docs/validation/telecom-browser-mcp-v0.2-diagnostics",
    )
    parser.add_argument("--signatures-dir", default="docs/failure-signatures/telecom-ui")
    parser.add_argument("--prioritization-dir", default="docs/prioritization/telecom-browser-mcp")
    parser.add_argument("--remediation-dir", default="docs/remediation/telecom-browser-mcp-v0.2")
    parser.add_argument("--investigations-dir", default="docs/investigations/runtime-transport")
    parser.add_argument("--output-dir", default="docs/closed-loop/telecom-browser-mcp")
    parser.add_argument("--max-batches", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    from telecom_browser_mcp.closed_loop import run_closed_loop_cycle

    args = _parse_args()
    result = run_closed_loop_cycle(
        validation_dir=Path(args.validation_dir),
        validation_diagnostics_dir=Path(args.validation_diagnostics_dir),
        signatures_dir=Path(args.signatures_dir),
        prioritization_dir=Path(args.prioritization_dir),
        remediation_dir=Path(args.remediation_dir),
        investigations_dir=Path(args.investigations_dir),
        output_dir=Path(args.output_dir),
        max_batches=args.max_batches,
    )
    sys.stderr.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
