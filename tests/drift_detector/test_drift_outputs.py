from pathlib import Path

from telecom_browser_mcp.system_drift_detector import run_system_drift_detector


def test_drift_detector_writes_required_artifacts(tmp_path: Path) -> None:
    src_root = tmp_path / "src/telecom_browser_mcp"
    src_root.mkdir(parents=True)
    (src_root / "__init__.py").write_text("", encoding="utf-8")
    (src_root / "server.py").write_text("from telecom_browser_mcp.tools import api\n", encoding="utf-8")
    (src_root / "tools.py").write_text("x=1\n", encoding="utf-8")

    out = tmp_path / "out"
    result = run_system_drift_detector(src_root=src_root, output_dir=out)

    assert result["drift_severity"] in {"low", "mild", "moderate", "severe"}
    ts = result["timestamp"]
    assert (out / f"{ts}--architecture-drift-report.json").exists()
    assert (out / f"{ts}--drift-scorecard.json").exists()
    assert (out / f"{ts}--dependency-drift.json").exists()
    assert (out / f"{ts}--module-boundary-violations.json").exists()
