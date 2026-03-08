from telecom_browser_mcp.failure_signature_extractor import extract_signature_candidates


def test_signature_extraction_rules() -> None:
    normalized = [
        {
            "contract_id": "LIFECYCLE::stale_selector_recovery",
            "tool_name": None,
            "signals_present": ["console"],
            "root_cause": "selector_stale_or_dom_drift",
            "selector_target": "answer_button",
            "dom_missing_target": True,
            "page_closed_before_action": False,
            "js_error_present": False,
            "request_failed_present": False,
            "diagnostics_gap_present": False,
            "bundle_health": "partial",
        }
    ]
    candidates = extract_signature_candidates(normalized)
    assert candidates
    assert candidates[0]["signature_name"] == "selector_stale_after_dom_refresh"


def test_signature_extraction_skips_js_signature_without_matching_root_cause() -> None:
    normalized = [
        {
            "contract_id": "TOOL::collect_browser_logs",
            "tool_name": "collect_browser_logs",
            "signals_present": ["page_errors"],
            "root_cause": "diagnostic_observation",
            "selector_target": None,
            "dom_missing_target": False,
            "page_closed_before_action": False,
            "js_error_present": True,
            "request_failed_present": False,
            "diagnostics_gap_present": False,
            "bundle_health": "partial",
        }
    ]
    candidates = extract_signature_candidates(normalized)
    assert not candidates


def test_signature_extraction_skips_diagnostics_gap_without_gap_root_cause() -> None:
    normalized = [
        {
            "contract_id": "TOOL::collect_browser_logs",
            "tool_name": "collect_browser_logs",
            "signals_present": [],
            "root_cause": "diagnostic_observation",
            "selector_target": None,
            "dom_missing_target": False,
            "page_closed_before_action": False,
            "js_error_present": False,
            "request_failed_present": False,
            "diagnostics_gap_present": True,
            "bundle_health": "partial",
        }
    ]
    candidates = extract_signature_candidates(normalized)
    assert not candidates
