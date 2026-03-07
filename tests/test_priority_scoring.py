from telecom_browser_mcp.failure_priority_scorer import score_signature


def test_priority_scoring_prefers_new_severe_failures() -> None:
    severe = {
        "signature_id": "SIG-100",
        "name": "selector_stale_after_dom_refresh",
        "category": "selector_stale_after_dom_refresh",
        "occurrence_count": 4,
        "contract_ids": ["LIFECYCLE::stale_selector_recovery"],
        "confidence_notes": "strong",
    }
    noisy = {
        "signature_id": "SIG-200",
        "name": "diagnostics_bundle_missing_on_failure",
        "category": "diagnostics_bundle_missing_on_failure",
        "occurrence_count": 2,
        "contract_ids": ["TOOL::open_app"],
        "confidence_notes": "weak",
    }
    severe_score = score_signature(severe, novelty_classification="new_signature")
    noisy_score = score_signature(noisy, novelty_classification="known_signature")
    assert severe_score["score"] > noisy_score["score"]
    assert severe_score["priority_bucket"] in {"P0", "P1"}
