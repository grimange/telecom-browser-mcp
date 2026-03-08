from telecom_browser_mcp.stability_governor import GovernorVerdictPlanner


def test_governor_verdict_critical_regression() -> None:
    scorecard = {"system_stability_score": 90.0}
    risks = [{"severity": "critical"}]
    regression = {"regression_detected": True}

    verdict = GovernorVerdictPlanner().decide(
        scorecard=scorecard,
        risks=risks,
        regression_detection=regression,
    )

    assert verdict["governor_verdict"] == "critical_regression"


def test_governor_verdict_stable_with_risks() -> None:
    scorecard = {"system_stability_score": 85.0}
    risks = [{"severity": "high"}]
    regression = {"regression_detected": False}

    verdict = GovernorVerdictPlanner().decide(
        scorecard=scorecard,
        risks=risks,
        regression_detection=regression,
    )

    assert verdict["governor_verdict"] == "stable_with_risks"
