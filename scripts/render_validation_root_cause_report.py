#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render root-cause markdown report from JSON summary")
    parser.add_argument("--root-cause-summary", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    payload = json.loads(Path(args.root_cause_summary).read_text(encoding="utf-8"))
    lines = [
        "# Validation Root Cause Report",
        "",
        "## Categories",
        "",
    ]
    categories = payload.get("categories", [])
    if not categories:
        lines.append("- none")
    for item in categories:
        lines.append(
            f"- `{item['category']}`: {item['count']} "
            f"(scenarios={len(item.get('scenarios', []))}, contracts={len(item.get('contracts', []))})"
        )
    lines.append("")
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
