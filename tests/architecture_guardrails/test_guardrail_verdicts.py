from telecom_browser_mcp.architecture_guardrails import GuardrailVerdictEngine


def test_guardrails_block_on_critical_violation() -> None:
    verdict = GuardrailVerdictEngine().decide(
        violations=[{"severity": "critical", "rule_id": "X"}]
    )
    assert verdict == "guardrails_block"


def test_guardrails_warn_on_non_critical_violations() -> None:
    verdict = GuardrailVerdictEngine().decide(
        violations=[{"severity": "moderate", "rule_id": "Y"}]
    )
    assert verdict == "guardrails_warn"


def test_guardrails_pass_with_no_violations() -> None:
    verdict = GuardrailVerdictEngine().decide(violations=[])
    assert verdict == "guardrails_pass"
