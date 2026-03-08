from telecom_browser_mcp.pipeline_governor import PipelineGovernor


def _base_collected() -> dict:
    return {
        "closed_loop": {
            "available": True,
            "cycle_verdict": "meaningful improvement achieved",
            "runtime_transport_classification": "resolved",
        },
        "stability": {"available": True, "stability_verdict": "stable"},
        "guardrails": {"available": True, "postcheck_verdict": "pass"},
        "drift": {"available": False, "drift_severity": "unknown", "blocked_subsystems": []},
    }


def test_global_verdict_blocked_by_architecture() -> None:
    collected = _base_collected()
    collected["guardrails"]["postcheck_verdict"] = "blocked"

    verdict = PipelineGovernor().decide(collected=collected, conflicts={"conflicts": []})

    assert verdict["global_verdict"] == "blocked_by_architecture"


def test_global_verdict_blocked_by_runtime_environment() -> None:
    collected = _base_collected()
    collected["closed_loop"]["runtime_transport_classification"] = "unresolved_ambiguity"

    verdict = PipelineGovernor().decide(collected=collected, conflicts={"conflicts": []})

    assert verdict["global_verdict"] == "blocked_by_runtime_environment"


def test_global_verdict_blocked_by_stability() -> None:
    collected = _base_collected()
    collected["stability"]["stability_verdict"] = "critical_regression"

    verdict = PipelineGovernor().decide(collected=collected, conflicts={"conflicts": []})

    assert verdict["global_verdict"] == "blocked_by_stability"


def test_global_verdict_safe_improvement() -> None:
    collected = _base_collected()

    verdict = PipelineGovernor().decide(collected=collected, conflicts={"conflicts": []})

    assert verdict["global_verdict"] == "safe_meaningful_improvement"
