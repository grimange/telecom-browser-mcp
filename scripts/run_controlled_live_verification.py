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
    parser = argparse.ArgumentParser(description="Run controlled live verification artifacts")
    parser.add_argument("--output-dir", default="docs/live-verification/telecom-browser-mcp")
    parser.add_argument("--evidence-dir", default="")
    parser.add_argument("--mcp-timeout-seconds", type=float, default=20.0)
    parser.add_argument("--mcp-step-timeout-seconds", type=float, default=8.0)
    return parser.parse_args()


def main() -> int:
    from telecom_browser_mcp.live_verification import run_controlled_live_verification

    args = _parse_args()
    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else None
    result = run_controlled_live_verification(
        output_dir=Path(args.output_dir),
        evidence_dir=evidence_dir,
        mcp_timeout_seconds=args.mcp_timeout_seconds,
        mcp_step_timeout_seconds=args.mcp_step_timeout_seconds,
    )
    sys.stderr.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
