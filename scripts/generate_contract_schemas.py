from __future__ import annotations

import json
from pathlib import Path

from telecom_browser_mcp.contracts.m1_contracts import generate_m1_schemas


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "docs" / "contracts" / "m1"
    out_dir.mkdir(parents=True, exist_ok=True)

    schemas = generate_m1_schemas()
    for tool_name, payload in schemas.items():
        path = out_dir / f"{tool_name}.schema.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
