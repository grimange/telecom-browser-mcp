from telecom_browser_mcp.signature_library_store import build_signature_library


def test_signature_deduplication_groups_same_family() -> None:
    candidates = [
        {
            "signature_name": "page_closed_before_action",
            "category": "page_closed_before_action",
            "contract_id": "LIFECYCLE::page_closed_or_detached",
            "tool_name": None,
            "trigger_signals": ["page_closed_before_action"],
            "supporting_signals": [],
            "common_root_cause": "page_closed_or_detached",
            "recommended_actions": ["re-acquire page"],
            "confidence_model": "strong",
            "representative_scenario": "page_detach_recovery",
        },
        {
            "signature_name": "page_closed_before_action",
            "category": "page_closed_before_action",
            "contract_id": "LIFECYCLE::page_closed_or_detached",
            "tool_name": None,
            "trigger_signals": ["page_closed_before_action"],
            "supporting_signals": [],
            "common_root_cause": "page_closed_or_detached",
            "recommended_actions": ["re-acquire page"],
            "confidence_model": "strong",
            "representative_scenario": "page_detach_recovery",
        },
    ]
    library = build_signature_library(candidates)
    assert len(library) == 1
    assert library[0]["occurrence_count"] == 2
