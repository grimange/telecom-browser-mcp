from telecom_browser_mcp.stability_governor import RegressionDetector


def test_contract_regression_detection_flags_regression() -> None:
    cycle_summary = {
        "baseline_before": "before.json",
        "baseline_after": "after.json",
    }
    improvement_delta = {
        "status": "regressed",
        "delta": {"non_pass_contracts": 2, "environment_blockers": 0},
    }
    risks = [{"risk_id": "RISK-REGRESSION-001", "severity": "critical"}]

    report = RegressionDetector().detect(
        cycle_summary=cycle_summary,
        improvement_delta=improvement_delta,
        risks=risks,
    )

    assert report["regression_detected"] is True
    assert report["new_critical_risks"] == ["RISK-REGRESSION-001"]
