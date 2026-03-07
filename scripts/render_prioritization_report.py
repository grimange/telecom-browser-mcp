#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render prioritization markdown report")
    parser.add_argument("--priority-summary", required=True)
    parser.add_argument("--ranking", required=True)
    parser.add_argument("--new-regressions", required=True)
    parser.add_argument("--recommended-batches", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    summary = json.loads(Path(args.priority_summary).read_text(encoding="utf-8"))
    ranking = json.loads(Path(args.ranking).read_text(encoding="utf-8"))
    regressions = json.loads(Path(args.new_regressions).read_text(encoding="utf-8"))
    batches = json.loads(Path(args.recommended_batches).read_text(encoding="utf-8"))
    ranked = ranking.get("ranked_signatures", [])[:5]
    batch_rows = batches.get("recommended_batches", [])[:5]

    lines = [
        "# Remediation Prioritization Report",
        "",
        "## Executive Summary",
        f"- total failures analyzed: {summary.get('total_failures_analyzed', 0)}",
        f"- total signatures: {summary.get('total_signatures', 0)}",
        "",
        "## Top Remediation Candidates",
    ]
    if not ranked:
        lines.append("- none")
    for item in ranked:
        lines.append(
            f"- `{item['signature_id']}` {item['signature_name']} "
            f"[{item['priority_bucket']}] score={item['score']}"
        )
    lines.extend(["", "## New Regressions"])
    reg_entries = regressions.get("entries", [])
    lines.append(f"- count: {len(reg_entries)}")
    lines.extend(["", "## Known Stable Failures"])
    lines.append(f"- count: {summary.get('new_vs_known', {}).get('known_signature', 0)}")
    lines.extend(["", "## Environment Noise"])
    lines.append(f"- count: {summary.get('domain_distribution', {}).get('environment_or_ci', 0)}")
    lines.extend(["", "## Suggested Next Pipelines"])
    if not batch_rows:
        lines.append("- none")
    for batch in batch_rows:
        lines.append(
            f"- `{batch['batch_id']}` {batch['priority_bucket']} "
            f"{batch['domain']} signatures={batch['signature_count']}"
        )
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
