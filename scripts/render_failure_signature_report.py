#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render failure signature markdown report")
    parser.add_argument("--library", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    library = json.loads(Path(args.library).read_text(encoding="utf-8"))
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    top = sorted(library, key=lambda item: item.get("occurrence_count", 0), reverse=True)[:5]

    lines = [
        "# Telecom UI Failure Signature Report",
        "",
        "## Executive Summary",
        f"- total signatures: {summary.get('total_signatures', 0)}",
        f"- total occurrences: {summary.get('total_occurrences', 0)}",
        "",
        "## Top Signature Families",
    ]
    if not top:
        lines.append("- none")
    for item in top:
        lines.append(
            f"- `{item['signature_id']}` {item['name']} "
            f"(count={item['occurrence_count']}, confidence={item['confidence_notes']})"
        )

    lines.extend(
        [
            "",
            "## Signature Quality",
            f"- high-confidence signatures: {summary.get('high_confidence_signatures', 0)}",
            "",
            "## Product vs Environment Failures",
            f"- product signatures: {summary.get('product_signatures', 0)}",
            f"- environment signatures: {summary.get('environment_signatures', 0)}",
            "",
            "## Diagnostics Gaps",
            f"- diagnostics gap signatures: {summary.get('diagnostics_gap_signatures', 0)}",
            "",
            "## Recommended Next Actions",
            "- expand signature families for telecom call-state races",
            "- add webrtc readiness signatures",
            "- increase contract-to-bundle linkage coverage",
            "",
        ]
    )
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
