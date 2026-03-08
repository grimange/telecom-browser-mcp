from telecom_browser_mcp.stability_governor import RiskAnalyzer


def test_environment_block_creates_high_browser_lifecycle_risk() -> None:
    scorecard = {"diagnostics_reliability_score": 95}
    cycle_summary = {"cycle_verdict": "blocked by environment"}
    improvement_delta = {
        "status": "unchanged",
        "classification": "environment blocked",
        "delta": {"environment_blockers": 1},
        "remediation_outcomes": {"blocked": 1},
    }
    batch_execution_results = {"selected_batches": []}

    risks = RiskAnalyzer().detect(
        scorecard=scorecard,
        cycle_summary=cycle_summary,
        improvement_delta=improvement_delta,
        batch_execution_results=batch_execution_results,
    )

    assert any(
        risk["severity"] == "high" and risk["dimension"] == "browser_lifecycle"
        for risk in risks
    )
