from telecom_browser_mcp.signature_signal_normalizer import normalize_failure_signal


def test_signal_normalization_selector_stale() -> None:
    row = {
        "contract_id": "LIFECYCLE::stale_selector_recovery",
        "validation_status": "INCONCLUSIVE",
        "primary_root_cause": "selector_stale_or_dom_drift",
        "collection_gaps": [],
        "supporting_signals": ["console"],
        "bundle_health": "partial",
    }
    normalized = normalize_failure_signal(row, bundle_manifest={"artifact_paths": {"trace": None}})
    assert normalized["selector_target"] == "answer_button"
    assert normalized["dom_missing_target"] is True
    assert normalized["diagnostics_gap_present"] is False


def test_signal_normalization_malformed_gap() -> None:
    row = {
        "contract_id": "TOOL::open_app",
        "validation_status": "PASS",
        "primary_root_cause": "diagnostics_collection_gap",
        "collection_gaps": ["manifest missing"],
        "supporting_signals": [],
        "bundle_health": "malformed",
    }
    normalized = normalize_failure_signal(row, bundle_manifest=None)
    assert normalized["diagnostics_gap_present"] is True


def test_signal_normalization_ignores_diagnostic_observation_error_signals() -> None:
    row = {
        "contract_id": "TOOL::collect_browser_logs",
        "validation_status": "PASS",
        "primary_root_cause": "diagnostic_observation",
        "collection_gaps": [],
        "supporting_signals": ["page_errors", "network"],
        "bundle_health": "partial",
        "bundle_status": "ok",
        "bundle_failure_classification": "diagnostic",
    }
    normalized = normalize_failure_signal(row, bundle_manifest={"artifact_paths": {}})
    assert normalized["js_error_present"] is False
    assert normalized["request_failed_present"] is False
    assert normalized["diagnostics_gap_present"] is False
