from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_interop_probe_failure_payload_includes_phase_and_preflight() -> None:
    proc = subprocess.run(
        [
            ".venv/bin/python",
            "scripts/run_mcp_interop_probe.py",
            "--dry-run-preflight",
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert proc.stdout.strip()
    payload_path = Path(proc.stdout.strip().splitlines()[-1])
    assert payload_path.exists()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert "preflight" in payload
    assert "evidence" in payload
    assert payload.get("classification") == "preflight_only"
