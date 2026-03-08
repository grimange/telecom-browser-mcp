import json
from pathlib import Path

from telecom_browser_mcp.pipeline_governor import run_pipeline_governor


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_live_verification_blocked_overrides_release_candidate(tmp_path: Path) -> None:
    closed_loop = tmp_path / "closed-loop"
    stability = tmp_path / "stability"
    guardrails = tmp_path / "guardrails"
    investigations = tmp_path / "investigations"
    release_hardening = tmp_path / "release-hardening"
    live_verification = tmp_path / "live-verification"
    out = tmp_path / "out"

    ts = "20260308T010203Z"
    _write_json(closed_loop / f"{ts}--cycle-summary.json", {"cycle_verdict": "stable enough for beta"})
    _write_json(closed_loop / f"{ts}--improvement-delta.json", {"delta": {"environment_blockers": 0}})
    _write_json(closed_loop / f"{ts}--batch-execution-results.json", {"selected_batches": []})
    _write_json(closed_loop / f"{ts}--transport-triage.json", {"classification": "resolved"})
    _write_json(stability / "20260308T020000Z--governor-verdict.json", {"governor_verdict": "stable"})
    _write_json(stability / "20260308T020000Z--stability-scorecard.json", {"system_stability_score": 95.0})
    _write_json(stability / "20260308T020000Z--detected-risks.json", [])
    _write_json(guardrails / "20260308T020000Z--precheck-verdict.json", {"verdict": "guardrails_pass"})
    _write_json(guardrails / "20260308T020000Z--postcheck-verdict.json", {"verdict": "guardrails_pass"})
    _write_json(investigations / "20260308T030000Z--runtime-transport-classification.json", {"classification": "resolved"})
    _write_json(release_hardening / "release-hardening-verdict.json", {"verdict": "release_ready"})
    _write_json(release_hardening / "release-check-results.json", {"checks": []})
    _write_json(release_hardening / "release-risk-register.json", {"risks": []})
    _write_json(
        live_verification / "live-verification-verdict.json",
        {
            "verdict": "blocked",
            "blocking_reasons": ["mcp initialize handshake timeout in live stdio probe"],
        },
    )

    result = run_pipeline_governor(
        closed_loop_dir=closed_loop,
        stability_dir=stability,
        guardrails_dir=guardrails,
        learning_dir=tmp_path / "learning",
        drift_dir=tmp_path / "drift",
        investigations_dir=investigations,
        release_hardening_dir=release_hardening,
        live_verification_dir=live_verification,
        output_dir=out,
    )

    assert result["global_verdict"] == "blocked_by_live_verification"
    verdict = json.loads((out / "governor-verdict.json").read_text(encoding="utf-8"))
    assert verdict["release_track_allowed"] is False
    assert verdict["recommended_global_action"] == "remediate_live_verification_blockers"
    assert "live_verification_blocked" in verdict["release_block_reason"]
