from __future__ import annotations

from typing import Any


def normalize_failure_signal(
    contract_row: dict[str, Any],
    *,
    bundle_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root_cause = str(contract_row.get("primary_root_cause", "unknown"))
    collection_gaps = list(contract_row.get("collection_gaps", []))
    supporting_signals = list(contract_row.get("supporting_signals", []))
    bundle_health = str(contract_row.get("bundle_health", "missing"))
    bundle_status = str(contract_row.get("bundle_status", "unknown"))
    bundle_failure_classification = str(contract_row.get("bundle_failure_classification", "unknown"))
    manifest_artifacts = (bundle_manifest or {}).get("artifact_paths", {})

    normalized = {
        "contract_id": contract_row.get("contract_id"),
        "validation_status": contract_row.get("validation_status"),
        "tool_name": _tool_from_contract(contract_row.get("contract_id")),
        "root_cause": root_cause,
        "selector_target": None,
        "dom_missing_target": False,
        "page_closed_before_action": root_cause == "page_closed_or_detached",
        "context_closed_during_wait": root_cause == "context_invalidated",
        "browser_unavailable": root_cause == "browser_unavailable",
        "js_error_present": (
            "page_errors" in supporting_signals
            and not (bundle_failure_classification == "diagnostic" and bundle_status == "ok")
        ),
        "request_failed_present": (
            "network" in supporting_signals
            and not (bundle_failure_classification == "diagnostic" and bundle_status == "ok")
        ),
        "trace_available": bool(manifest_artifacts.get("trace")),
        "screenshot_missing_due_to_page_death": (
            not manifest_artifacts.get("screenshot")
            and any("page" in gap and "closed" in gap for gap in collection_gaps)
        ),
        "cleanup_succeeded": False,
        "diagnostics_gap_present": (
            bundle_health in {"missing", "malformed"}
            or (
                bool(collection_gaps)
                and not (bundle_failure_classification == "diagnostic" and bundle_status == "ok")
            )
        ),
        "bundle_health": bundle_health,
        "bundle_status": bundle_status,
        "bundle_failure_classification": bundle_failure_classification,
        "collection_gaps": collection_gaps,
        "signals_present": supporting_signals,
    }

    if root_cause == "selector_stale_or_dom_drift":
        normalized["selector_target"] = "answer_button"
        normalized["dom_missing_target"] = True
    return normalized


def normalize_failure_signals(
    contract_rows: list[dict[str, Any]],
    manifest_by_contract: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    manifest_by_contract = manifest_by_contract or {}
    return [
        normalize_failure_signal(
            row,
            bundle_manifest=manifest_by_contract.get(str(row.get("contract_id"))),
        )
        for row in contract_rows
    ]


def _tool_from_contract(contract_id: Any) -> str | None:
    value = str(contract_id or "")
    if value.startswith("TOOL::"):
        return value.split("::", 1)[1]
    return None
