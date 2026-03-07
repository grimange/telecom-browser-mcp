from telecom_browser_mcp.validation.root_cause_classifier import classify_root_cause
from telecom_browser_mcp.validation.validation_diagnostics_ingestor import BundleIngestion


def _bundle(scenario_id: str, *, health: str = "partial") -> BundleIngestion:
    return BundleIngestion(
        scenario_id=scenario_id,
        bundle_path="/tmp/bundle",
        manifest_path="/tmp/bundle/manifest.json",
        signals_present=[],
        signals_missing=[],
        collection_gaps=[],
        cleanup_status="unknown",
        bundle_health=health,
        failure_classification="session",
        status="failed",
    )


def test_root_cause_from_scenario_names() -> None:
    assert classify_root_cause(_bundle("stale_selector_recovery")) == "selector_stale_or_dom_drift"
    assert classify_root_cause(_bundle("page_detach_recovery")) == "page_closed_or_detached"
    assert classify_root_cause(_bundle("context_closure_recovery")) == "context_invalidated"
    assert classify_root_cause(_bundle("browser_crash_recovery")) == "browser_unavailable"


def test_root_cause_missing_bundle() -> None:
    assert classify_root_cause(_bundle("unknown", health="missing")) == "diagnostics_collection_gap"
