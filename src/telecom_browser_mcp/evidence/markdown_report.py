from __future__ import annotations

from pathlib import Path


def write_markdown_report(session, summary: dict) -> str:
    report_path = Path(session.artifacts_dir) / "report.md"
    lines = [
        "# telecom-browser-mcp evidence report",
        "",
        f"- session_id: {session.session_id}",
        f"- run_id: {session.run_id}",
        f"- adapter: {session.adapter_name}:{session.adapter_version}",
        "",
        "## Summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- {key}: {value}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(report_path)
