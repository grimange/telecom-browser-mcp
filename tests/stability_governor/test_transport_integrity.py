from telecom_browser_mcp.stability_governor import GovernorVerdictPlanner


def test_transport_instability_triggers_instability_detected() -> None:
    scorecard = {
        "system_stability_score": 55.0,
    }
    risks = [
        {"severity": "high"},
        {"severity": "high"},
    ]
    regression = {"regression_detected": False}

    verdict = GovernorVerdictPlanner().decide(
        scorecard=scorecard,
        risks=risks,
        regression_detection=regression,
    )

    assert verdict["governor_verdict"] == "instability_detected"
