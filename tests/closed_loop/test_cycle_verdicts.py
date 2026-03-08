from telecom_browser_mcp.closed_loop import NextCyclePlanner


def test_cycle_verdict_blocked_by_diagnostics() -> None:
    delta = {
        "status": "unchanged",
        "diagnostics_coverage_score": 7.14,
        "remediation_outcomes": {"blocked": 0},
        "after": {"non_pass_contracts": 4},
    }

    verdict = NextCyclePlanner().evaluate_cycle(delta)
    assert verdict["cycle_verdict"] == "blocked by diagnostics"


def test_cycle_verdict_regression_detected() -> None:
    delta = {
        "status": "regressed",
        "diagnostics_coverage_score": 15.0,
        "remediation_outcomes": {"blocked": 0},
        "after": {"non_pass_contracts": 8},
    }

    verdict = NextCyclePlanner().evaluate_cycle(delta)
    assert verdict["cycle_verdict"] == "regression detected"


def test_cycle_verdict_quarantines_sandbox_transport_blocker() -> None:
    delta = {
        "status": "unchanged",
        "diagnostics_coverage_score": 100.0,
        "remediation_outcomes": {"blocked": 1},
        "after": {"non_pass_contracts": 0},
        "runtime_environment_quarantined": True,
    }

    verdict = NextCyclePlanner().evaluate_cycle(delta)
    assert verdict["cycle_verdict"] == "stable enough for beta"
