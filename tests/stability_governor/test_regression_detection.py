from pathlib import Path

from telecom_browser_mcp.stability_governor import StabilityGovernorReadinessEvaluator


def test_readiness_uses_latest_cycle_timestamp(tmp_path: Path) -> None:
    closed_loop = tmp_path / "closed-loop"
    closed_loop.mkdir(parents=True, exist_ok=True)

    older = "20260307T220000Z"
    newer = "20260307T230000Z"

    (closed_loop / f"{older}--cycle-summary.json").write_text("{}", encoding="utf-8")
    (closed_loop / f"{newer}--cycle-summary.json").write_text("{}", encoding="utf-8")
    (closed_loop / f"{newer}--batch-execution-results.json").write_text("{}", encoding="utf-8")
    (closed_loop / f"{newer}--improvement-delta.json").write_text("{}", encoding="utf-8")
    (closed_loop / f"{newer}--cycle-verdict.md").write_text("# Cycle Verdict\n", encoding="utf-8")

    readiness = StabilityGovernorReadinessEvaluator(closed_loop_dir=closed_loop).evaluate()

    assert readiness.ok is True
    assert readiness.cycle_timestamp == newer
