from telecom_browser_mcp.closed_loop import PostRemediationDeltaAnalyzer


def test_improvement_delta_identifies_partial_improvement() -> None:
    before = {
        "timestamp": "20260307T113620Z",
        "total_fail": 2,
        "total_partial": 3,
        "total_inconclusive": 2,
        "environment_blockers": [],
    }
    after = {
        "timestamp": "20260307T123026Z",
        "total_fail": 0,
        "total_partial": 2,
        "total_inconclusive": 2,
        "environment_blockers": [],
    }
    enriched = {"diagnostics_coverage_score": 12.5}
    ranking = {"ranked_signatures": [{"signature_name": "selector_stale_after_dom_refresh"}]}
    batch_status = {"C_telecom_flow": "fixed", "D_diagnostics_and_bundles": "partially fixed"}

    delta = PostRemediationDeltaAnalyzer().analyze(
        before_validation=before,
        after_validation=after,
        enriched_summary=enriched,
        ranking=ranking,
        batch_status=batch_status,
    )

    assert delta["status"] == "fixed"
    assert delta["delta"]["non_pass_contracts"] == -3


def test_improvement_delta_quarantines_sandbox_runtime_transport() -> None:
    before = {
        "timestamp": "20260307T113620Z",
        "total_fail": 0,
        "total_partial": 2,
        "total_inconclusive": 2,
        "environment_blockers": [],
    }
    after = {
        "timestamp": "20260307T123026Z",
        "total_fail": 0,
        "total_partial": 2,
        "total_inconclusive": 2,
        "environment_blockers": ["interop probe timed out"],
    }
    enriched = {"diagnostics_coverage_score": 100.0}
    ranking = {"ranked_signatures": []}
    batch_status = {"RB-001": "blocked by environment"}

    delta = PostRemediationDeltaAnalyzer().analyze(
        before_validation=before,
        after_validation=after,
        enriched_summary=enriched,
        ranking=ranking,
        batch_status=batch_status,
        runtime_transport_classification={"classification": "sandbox_only_execution_blocker"},
    )

    assert delta["runtime_environment_quarantined"] is True
    assert delta["classification"] == "runtime transport sandbox blocked (quarantined)"
