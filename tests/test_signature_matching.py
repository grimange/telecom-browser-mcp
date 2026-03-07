from telecom_browser_mcp.failure_signature_matcher import match_signature


def test_signature_matching_strength_exact() -> None:
    signal = {"selector_target": "answer_button", "dom_missing_target": True}
    signatures = [
        {
            "signature_id": "SIG-001",
            "trigger_signals": ["selector_target", "dom_missing_target"],
            "recommended_actions": ["refresh selector"],
        }
    ]
    match = match_signature(signal, signatures)
    assert match["signature_id"] == "SIG-001"
    assert match["match_strength"] == "exact"
