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
    parser = argparse.ArgumentParser(description="Run pipeline governor orchestrator artifacts")
    parser.add_argument("--closed-loop-dir", default="docs/closed-loop/telecom-browser-mcp")
    parser.add_argument("--stability-dir", default="docs/stability-governor/telecom-browser-mcp")
    parser.add_argument("--guardrails-dir", default="docs/architecture-guardrails/telecom-browser-mcp")
    parser.add_argument("--learning-dir", default="docs/cross-cycle-learning/telecom-browser-mcp")
    parser.add_argument("--drift-dir", default="docs/drift-detection/telecom-browser-mcp")
    parser.add_argument("--investigations-dir", default="docs/investigations/runtime-transport")
    parser.add_argument("--release-hardening-dir", default="docs/release-hardening/telecom-browser-mcp")
    parser.add_argument("--live-verification-dir", default="docs/live-verification/telecom-browser-mcp")
    parser.add_argument("--output-dir", default="docs/pipeline-governor/telecom-browser-mcp")
    return parser.parse_args()


def main() -> int:
    from telecom_browser_mcp.pipeline_governor import run_pipeline_governor

    args = _parse_args()
    result = run_pipeline_governor(
        closed_loop_dir=Path(args.closed_loop_dir),
        stability_dir=Path(args.stability_dir),
        guardrails_dir=Path(args.guardrails_dir),
        learning_dir=Path(args.learning_dir),
        drift_dir=Path(args.drift_dir),
        investigations_dir=Path(args.investigations_dir),
        release_hardening_dir=Path(args.release_hardening_dir),
        live_verification_dir=Path(args.live_verification_dir),
        output_dir=Path(args.output_dir),
    )
    sys.stderr.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
