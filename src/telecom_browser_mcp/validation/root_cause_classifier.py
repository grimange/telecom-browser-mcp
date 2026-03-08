from __future__ import annotations

from telecom_browser_mcp.validation.validation_diagnostics_ingestor import BundleIngestion

ROOT_CAUSE_ORDER = [
    "selector_stale_or_dom_drift",
    "page_closed_or_detached",
    "context_invalidated",
    "browser_unavailable",
    "diagnostic_observation",
    "javascript_runtime_error",
    "network_failure",
    "cleanup_failure",
    "diagnostics_collection_gap",
    "environment_blocked",
    "contract_ambiguous",
    "unknown",
]


def classify_root_cause(bundle: BundleIngestion) -> str:
    scenario = bundle.scenario_id
    if bundle.bundle_health in {"missing", "malformed"}:
        return "diagnostics_collection_gap"
    if bundle.status == "ok" and bundle.failure_classification in {"none", "diagnostic"}:
        return "diagnostic_observation"
    if bundle.failure_classification == "diagnostic" and bundle.status == "ok":
        return "diagnostic_observation"
    if "stale_selector" in scenario:
        return "selector_stale_or_dom_drift"
    if "page_detach" in scenario or "page_closed" in scenario:
        return "page_closed_or_detached"
    if "context_closure" in scenario or "context_invalid" in scenario:
        return "context_invalidated"
    if "browser_crash" in scenario or "browser_unavailable" in scenario:
        return "browser_unavailable"
    if "page_errors" in bundle.signals_present:
        return "javascript_runtime_error"
    if "network" in bundle.signals_present and "network" not in bundle.signals_missing:
        return "network_failure"
    if bundle.collection_gaps:
        return "diagnostics_collection_gap"
    if bundle.failure_classification == "environment":
        return "environment_blocked"
    if bundle.failure_classification == "unknown":
        return "contract_ambiguous"
    return "unknown"
