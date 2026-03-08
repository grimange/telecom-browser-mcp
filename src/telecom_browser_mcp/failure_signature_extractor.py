from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def extract_signature_candidates(normalized_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    candidates: list[dict[str, Any]] = []
    for row in normalized_rows:
        for name, matcher, category in _signature_rules():
            if not matcher(row):
                continue
            contract_id = row.get("contract_id")
            candidates.append(
                {
                    "signature_name": name,
                    "category": category,
                    "contract_id": contract_id,
                    "tool_name": row.get("tool_name"),
                    "trigger_signals": _trigger_signals(name, row),
                    "supporting_signals": row.get("signals_present", []),
                    "common_root_cause": row.get("root_cause", "unknown"),
                    "recommended_actions": _recommended_actions(name),
                    "confidence_model": _confidence(name, row),
                    "representative_scenario": _scenario_from_contract(contract_id),
                    "seen_at": now,
                }
            )
            break
    return candidates


def _match_selector_stale(row: dict[str, Any]) -> bool:
    return bool(row.get("dom_missing_target") and row.get("selector_target"))


def _match_page_closed(row: dict[str, Any]) -> bool:
    return bool(row.get("page_closed_before_action"))


def _match_javascript_runtime_error(row: dict[str, Any]) -> bool:
    return bool(row.get("js_error_present") and row.get("root_cause") == "javascript_runtime_error")


def _match_network_failure(row: dict[str, Any]) -> bool:
    return bool(row.get("request_failed_present") and row.get("root_cause") == "network_failure")


def _match_diagnostics_gap(row: dict[str, Any]) -> bool:
    return bool(
        row.get("diagnostics_gap_present")
        and row.get("root_cause") == "diagnostics_collection_gap"
    )


def _confidence(name: str, row: dict[str, Any]) -> str:
    if name in {"selector_stale_after_dom_refresh", "page_closed_before_action"}:
        return "strong"
    if name in {"javascript_runtime_error", "network_failure_ui_timeout"}:
        return "moderate"
    if row.get("bundle_health") == "missing":
        return "exact"
    return "weak"


def _trigger_signals(name: str, row: dict[str, Any]) -> list[str]:
    mapping = {
        "selector_stale_after_dom_refresh": ["selector_target", "dom_missing_target"],
        "page_closed_before_action": ["page_closed_before_action"],
        "javascript_runtime_error": ["js_error_present"],
        "network_failure_ui_timeout": ["request_failed_present"],
        "diagnostics_bundle_missing_on_failure": ["diagnostics_gap_present"],
    }
    keys = mapping.get(name, [])
    return [key for key in keys if row.get(key)]


def _recommended_actions(name: str) -> list[str]:
    actions = {
        "selector_stale_after_dom_refresh": ["refresh selector before click", "add DOM-ready guard"],
        "page_closed_before_action": ["re-acquire page handle", "retry action after page liveness check"],
        "javascript_runtime_error": ["inspect page-errors.json", "stabilize UI state transition handlers"],
        "network_failure_ui_timeout": ["inspect network.json failures", "add bounded retry for failed requests"],
        "diagnostics_bundle_missing_on_failure": ["wire diagnostics capture earlier", "validate manifest generation"],
    }
    return actions.get(name, ["review diagnostics bundle"])


def _scenario_from_contract(contract_id: Any) -> str:
    value = str(contract_id or "")
    map_contract = {
        "LIFECYCLE::stale_selector_recovery": "stale_selector_recovery",
        "LIFECYCLE::crash_recovery": "browser_crash_recovery",
        "LIFECYCLE::context_closure_recovery": "context_closure_recovery",
        "LIFECYCLE::page_closed_or_detached": "page_detach_recovery",
    }
    return map_contract.get(value, "validation_contract_row")


def _signature_rules() -> list[tuple[str, Any, str]]:
    return [
        ("selector_stale_after_dom_refresh", _match_selector_stale, "selector_stale_after_dom_refresh"),
        ("page_closed_before_action", _match_page_closed, "page_closed_before_action"),
        ("javascript_runtime_error", _match_javascript_runtime_error, "javascript_runtime_error"),
        ("network_failure_ui_timeout", _match_network_failure, "network_failure_ui_timeout"),
        ("diagnostics_bundle_missing_on_failure", _match_diagnostics_gap, "diagnostics_bundle_missing_on_failure"),
    ]
