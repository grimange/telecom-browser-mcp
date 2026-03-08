from pathlib import Path

from telecom_browser_mcp.closed_loop import CycleReadinessEvaluator


def _touch(path: Path, content: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_readiness_check_passes_when_required_inputs_exist(tmp_path: Path) -> None:
    validation_dir = tmp_path / "validation"
    diagnostics_dir = tmp_path / "diagnostics"
    signatures_dir = tmp_path / "signatures"
    prioritization_dir = tmp_path / "prioritization"
    remediation_dir = tmp_path / "remediation"

    _touch(validation_dir / "20260307T123026Z--validation-summary.json")
    _touch(diagnostics_dir / "enriched-validation-summary.json")
    _touch(diagnostics_dir / "root-cause-summary.json")
    _touch(signatures_dir / "20260307T133147Z--failure-signatures.json")
    _touch(prioritization_dir / "20260307T134459Z--signature-priority-ranking.json")
    _touch(prioritization_dir / "20260307T134459Z--recommended-batches.json")
    _touch(remediation_dir / "20260307T123302Z--batch-status.json")
    _touch(remediation_dir / "20260307T123302Z--rerun-summary.json")

    result = CycleReadinessEvaluator(
        validation_dir=validation_dir,
        validation_diagnostics_dir=diagnostics_dir,
        signatures_dir=signatures_dir,
        prioritization_dir=prioritization_dir,
        remediation_dir=remediation_dir,
    ).evaluate()
    assert result.ok is True
    assert all(result.checks.values())
