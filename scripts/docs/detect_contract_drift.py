from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_catalog_by_name(path: Path) -> dict[str, dict[str, Any]]:
    payload = _read_json(path)
    tools = payload.get("tools", [])
    return {tool["name"]: tool for tool in tools}


def detect_delta(previous: dict[str, dict[str, Any]], current: dict[str, dict[str, Any]]) -> dict[str, Any]:
    prev_names = set(previous.keys())
    curr_names = set(current.keys())

    added = sorted(curr_names - prev_names)
    removed = sorted(prev_names - curr_names)
    changed: list[dict[str, Any]] = []

    for name in sorted(prev_names & curr_names):
        p = previous[name]
        c = current[name]

        p_required = sorted(p.get("required_fields", []))
        c_required = sorted(c.get("required_fields", []))
        p_optional = sorted(p.get("optional_fields", []))
        c_optional = sorted(c.get("optional_fields", []))

        diffs: dict[str, Any] = {}
        if p_required != c_required:
            diffs["required_fields"] = {"before": p_required, "after": c_required}
        if p_optional != c_optional:
            diffs["optional_fields"] = {"before": p_optional, "after": c_optional}

        if diffs:
            classification = "breaking" if any(
                field for field in c_required if field not in p_required
            ) else "additive"
            changed.append({"tool": name, "classification": classification, "diff": diffs})

    if removed:
        top_classification = "breaking"
    elif changed and any(c["classification"] == "breaking" for c in changed):
        top_classification = "breaking"
    elif added:
        top_classification = "additive"
    else:
        top_classification = "metadata_only"

    return {
        "classification": top_classification,
        "added_tools": added,
        "removed_tools": removed,
        "changed_tools": changed,
    }


def render_markdown(delta: dict[str, Any]) -> str:
    lines = [
        "# Documentation Drift Findings",
        "",
        f"- Overall classification: `{delta['classification']}`",
        f"- Added tools: {', '.join(delta['added_tools']) if delta['added_tools'] else 'none'}",
        f"- Removed tools: {', '.join(delta['removed_tools']) if delta['removed_tools'] else 'none'}",
        "",
        "## Changed Tools",
    ]

    if not delta["changed_tools"]:
        lines.append("- none")
    else:
        for item in delta["changed_tools"]:
            lines.append(f"- `{item['tool']}` ({item['classification']})")

    lines.append("")
    return "\n".join(lines)


def latest_previous_catalog(generated_root: Path, current_out_dir: Path) -> Path | None:
    if not generated_root.exists():
        return None
    candidates = sorted(
        [p for p in generated_root.iterdir() if p.is_dir() and p != current_out_dir],
        key=lambda p: p.name,
    )
    for candidate in reversed(candidates):
        catalog = candidate / "tool-catalog.json"
        if catalog.exists():
            return catalog
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-catalog", required=True)
    parser.add_argument("--generated-root", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    current_catalog_path = Path(args.current_catalog)
    generated_root = Path(args.generated_root)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    current_out_dir = current_catalog_path.parent

    previous_catalog_path = latest_previous_catalog(generated_root, current_out_dir)

    if previous_catalog_path is None:
        delta = {
            "classification": "metadata_only",
            "added_tools": [],
            "removed_tools": [],
            "changed_tools": [],
            "note": "no previous generated catalog found",
        }
    else:
        current_catalog = _load_catalog_by_name(current_catalog_path)
        previous_catalog = _load_catalog_by_name(previous_catalog_path)
        delta = detect_delta(previous_catalog, current_catalog)
        delta["previous_catalog"] = str(previous_catalog_path)

    _write_json(out_json, delta)
    out_md.write_text(render_markdown(delta), encoding="utf-8")


if __name__ == "__main__":
    main()
