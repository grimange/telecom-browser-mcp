#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run raw MCP stdio initialize/tools-list handshake probe")
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--step-timeout-seconds", type=float, default=8.0)
    parser.add_argument("--output-path", default="")
    return parser.parse_args()


def main() -> int:
    from telecom_browser_mcp.mcp_handshake_probe import run_mcp_handshake_probe

    args = _parse_args()
    output_path = Path(args.output_path) if args.output_path else None
    path = run_mcp_handshake_probe(
        timeout_seconds=args.timeout_seconds,
        step_timeout_seconds=args.step_timeout_seconds,
        output_path=output_path,
    )
    print(str(path))
    payload = __import__("json").loads(path.read_text(encoding="utf-8"))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
