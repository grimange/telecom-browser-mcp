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
    parser = argparse.ArgumentParser(description="Run architecture guardrails engine artifacts")
    parser.add_argument("--src-root", default="src/telecom_browser_mcp")
    parser.add_argument("--closed-loop-dir", default="docs/closed-loop/telecom-browser-mcp")
    parser.add_argument("--output-dir", default="docs/architecture-guardrails/telecom-browser-mcp")
    return parser.parse_args()


def main() -> int:
    from telecom_browser_mcp.architecture_guardrails import run_architecture_guardrails

    args = _parse_args()
    result = run_architecture_guardrails(
        src_root=Path(args.src_root),
        closed_loop_dir=Path(args.closed_loop_dir),
        output_dir=Path(args.output_dir),
    )
    sys.stderr.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
