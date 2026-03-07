from telecom_browser_mcp.signature_regression_detector import classify_known_vs_new


def test_known_vs_new_classification_detects_regression() -> None:
    previous = [
        {"name": "selector_stale_after_dom_refresh", "category": "selector_stale_after_dom_refresh", "occurrence_count": 1}
    ]
    current = [
        {"signature_id": "SIG-001", "name": "selector_stale_after_dom_refresh", "category": "selector_stale_after_dom_refresh", "occurrence_count": 3}
    ]
    rows = classify_known_vs_new(current, previous)
    assert rows[0].classification == "known_but_regressing"
    assert rows[0].delta == 2
