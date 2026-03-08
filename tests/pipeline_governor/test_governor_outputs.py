import json
from pathlib import Path

from telecom_browser_mcp.pipeline_governor import run_pipeline_governor


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_pipeline_governor_writes_required_outputs(tmp_path: Path) -> None:
    closed_loop = tmp_path / "closed-loop"
    stability = tmp_path / "stability"
    investigations = tmp_path / "investigations"
    out = tmp_path / "out"

    ts = "20260308T010203Z"
    _write_json(
        closed_loop / f"{ts}--cycle-summary.json",
        {
            "cycle_verdict": "partial improvement continue",
            "environment_blockers": ["sandbox_transport"],
        },
    )
    _write_json(
        closed_loop / f"{ts}--improvement-delta.json",
        {"delta": {"environment_blockers": 1}, "status": "partially improved"},
    )
    _write_json(
        closed_loop / f"{ts}--batch-execution-results.json",
        {"selected_batches": [{"batch_id": "BATCH-001"}]},
    )
    _write_json(closed_loop / f"{ts}--transport-triage.json", {"classification": "resolved"})

    _write_json(stability / "20260308T020000Z--governor-verdict.json", {"governor_verdict": "stable"})
    _write_json(stability / "20260308T020000Z--stability-scorecard.json", {"system_stability_score": 88.0})
    _write_json(stability / "20260308T020000Z--detected-risks.json", [])
    _write_json(
        investigations / "20260308T030000Z--runtime-transport-classification.json",
        {"classification": "resolved"},
    )

    result = run_pipeline_governor(
        closed_loop_dir=closed_loop,
        stability_dir=stability,
        guardrails_dir=tmp_path / "guardrails",
        learning_dir=tmp_path / "learning",
        drift_dir=tmp_path / "drift",
        investigations_dir=investigations,
        output_dir=out,
    )

    assert result["global_verdict"] == "partial_improvement_continue"
    for file_name in [
        "governor-state.json",
        "governor-verdict.json",
        "next-pipeline-actions.json",
        "pipeline-conflicts.json",
        "governor-cycle-plan.md",
        "governor-decision-log.md",
        "pipeline-conflict-resolution.md",
        "global-cycle-verdict.md",
        "next-run-instructions.md",
    ]:
        assert (out / file_name).exists()


def test_pipeline_governor_allows_closed_loop_when_guardrails_pass(tmp_path: Path) -> None:
    closed_loop = tmp_path / "closed-loop"
    stability = tmp_path / "stability"
    guardrails = tmp_path / "guardrails"
    investigations = tmp_path / "investigations"
    out = tmp_path / "out"

    ts = "20260308T010203Z"
    _write_json(closed_loop / f"{ts}--cycle-summary.json", {"cycle_verdict": "stable enough for beta"})
    _write_json(closed_loop / f"{ts}--improvement-delta.json", {"delta": {"environment_blockers": 0}, "status": "unchanged"})
    _write_json(closed_loop / f"{ts}--batch-execution-results.json", {"selected_batches": []})
    _write_json(closed_loop / f"{ts}--transport-triage.json", {"classification": "resolved"})

    _write_json(stability / "20260308T020000Z--governor-verdict.json", {"governor_verdict": "stable_with_risks"})
    _write_json(stability / "20260308T020000Z--stability-scorecard.json", {"system_stability_score": 90.0})
    _write_json(stability / "20260308T020000Z--detected-risks.json", [])

    _write_json(guardrails / "20260308T020000Z--precheck-verdict.json", {"verdict": "guardrails_pass"})
    _write_json(guardrails / "20260308T020000Z--postcheck-verdict.json", {"verdict": "guardrails_pass"})
    _write_json(investigations / "20260308T030000Z--runtime-transport-classification.json", {"classification": "sandbox_only_execution_blocker"})

    run_pipeline_governor(
        closed_loop_dir=closed_loop,
        stability_dir=stability,
        guardrails_dir=guardrails,
        learning_dir=tmp_path / "learning",
        drift_dir=tmp_path / "drift",
        investigations_dir=investigations,
        output_dir=out,
    )

    next_actions = json.loads((out / "next-pipeline-actions.json").read_text(encoding="utf-8"))
    blocked_pipelines = {row["pipeline"] for row in next_actions["blocked_actions"]}
    assert "closed_loop_validation_remediation" not in blocked_pipelines
