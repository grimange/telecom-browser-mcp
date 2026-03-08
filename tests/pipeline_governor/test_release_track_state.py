import json
from pathlib import Path

from telecom_browser_mcp.pipeline_governor import run_pipeline_governor


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_release_candidate_inputs(base: Path) -> tuple[Path, Path, Path, Path, Path]:
    closed_loop = base / "closed-loop"
    stability = base / "stability"
    guardrails = base / "guardrails"
    investigations = base / "investigations"
    release_hardening = base / "release-hardening"

    ts = "20260308T010203Z"
    _write_json(closed_loop / f"{ts}--cycle-summary.json", {"cycle_verdict": "stable enough for beta"})
    _write_json(closed_loop / f"{ts}--improvement-delta.json", {"delta": {"environment_blockers": 0}})
    _write_json(closed_loop / f"{ts}--batch-execution-results.json", {"selected_batches": []})
    _write_json(closed_loop / f"{ts}--transport-triage.json", {"classification": "resolved"})

    _write_json(stability / "20260308T020000Z--governor-verdict.json", {"governor_verdict": "stable"})
    _write_json(stability / "20260308T020000Z--stability-scorecard.json", {"system_stability_score": 94.0})
    _write_json(stability / "20260308T020000Z--detected-risks.json", [])

    _write_json(guardrails / "20260308T020000Z--precheck-verdict.json", {"verdict": "guardrails_pass"})
    _write_json(guardrails / "20260308T020000Z--postcheck-verdict.json", {"verdict": "guardrails_pass"})
    _write_json(investigations / "20260308T030000Z--runtime-transport-classification.json", {"classification": "resolved"})
    return closed_loop, stability, guardrails, investigations, release_hardening


def test_release_ready_allows_release_progression(tmp_path: Path) -> None:
    closed_loop, stability, guardrails, investigations, release_hardening = _seed_release_candidate_inputs(tmp_path)
    out = tmp_path / "out"
    _write_json(release_hardening / "release-hardening-verdict.json", {"verdict": "release_ready"})
    _write_json(release_hardening / "release-check-results.json", {"checks": []})
    _write_json(release_hardening / "release-risk-register.json", {"risks": []})

    result = run_pipeline_governor(
        closed_loop_dir=closed_loop,
        stability_dir=stability,
        guardrails_dir=guardrails,
        learning_dir=tmp_path / "learning",
        drift_dir=tmp_path / "drift",
        investigations_dir=investigations,
        release_hardening_dir=release_hardening,
        output_dir=out,
    )

    assert result["global_verdict"] == "release_candidate"
    verdict = json.loads((out / "governor-verdict.json").read_text(encoding="utf-8"))
    assert verdict["release_track_allowed"] is True
    next_actions = json.loads((out / "next-pipeline-actions.json").read_text(encoding="utf-8"))
    assert any(row["pipeline"] == "release_progression" for row in next_actions["allowed_actions"])


def test_missing_release_artifacts_do_not_crash_and_mark_unavailable(tmp_path: Path) -> None:
    closed_loop, stability, guardrails, investigations, release_hardening = _seed_release_candidate_inputs(tmp_path)
    out = tmp_path / "out"

    result = run_pipeline_governor(
        closed_loop_dir=closed_loop,
        stability_dir=stability,
        guardrails_dir=guardrails,
        learning_dir=tmp_path / "learning",
        drift_dir=tmp_path / "drift",
        investigations_dir=investigations,
        release_hardening_dir=release_hardening,
        output_dir=out,
    )

    assert result["global_verdict"] == "release_hardening_incomplete"
    verdict = json.loads((out / "governor-verdict.json").read_text(encoding="utf-8"))
    assert verdict["release_hardening_verdict"] == "release_hardening_not_available"
    assert verdict["release_track_allowed"] is False
