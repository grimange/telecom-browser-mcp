from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_validate_script_keeps_stdout_clean(tmp_path: Path) -> None:
    validation_dir = tmp_path / "validation"
    validation_dir.mkdir()
    (validation_dir / "20260307T000000Z--validation-summary.json").write_text(
        json.dumps({"timestamp": "20260307T000000Z"}),
        encoding="utf-8",
    )
    (validation_dir / "20260307T000000Z--contract-matrix.json").write_text(
        json.dumps([{"contract_id": "LIFECYCLE::crash_recovery", "validation_status": "PASS"}]),
        encoding="utf-8",
    )
    lifecycle_results = tmp_path / "lifecycle-fault-results.json"
    lifecycle_results.write_text(
        json.dumps({"results": [{"name": "browser_crash_recovery"}]}),
        encoding="utf-8",
    )
    output_dir = tmp_path / "out"

    proc = subprocess.run(
        [
            ".venv/bin/python",
            "scripts/validate_v0_2_contracts.py",
            "--validation-dir",
            str(validation_dir),
            "--lifecycle-results",
            str(lifecycle_results),
            "--output-dir",
            str(output_dir),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert proc.stdout == ""
