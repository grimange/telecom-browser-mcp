from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from telecom_browser_mcp.validation.root_cause_classifier import classify_root_cause
from telecom_browser_mcp.validation.validation_diagnostics_ingestor import BundleIngestion

SCENARIO_TO_CONTRACT = {
    "browser_crash_recovery": "LIFECYCLE::crash_recovery",
    "stale_selector_recovery": "LIFECYCLE::stale_selector_recovery",
    "context_closure_recovery": "LIFECYCLE::context_closure_recovery",
    "page_detach_recovery": "LIFECYCLE::page_closed_or_detached",
    "parallel_session_isolation": "LIFECYCLE::parallel_session_isolation",
    "collect-browser-logs": "TOOL::collect_browser_logs",
    "collect-debug-bundle": "TOOL::collect_debug_bundle",
    "open-app-failure": "TOOL::open_app",
    "wait-for-ready-failure": "TOOL::wait_for_ready",
    "wait-for-registration-failure": "TOOL::wait_for_registration",
    "wait-for-incoming-call-failure": "TOOL::wait_for_incoming_call",
    "answer-call-failure": "TOOL::answer_call",
    "diagnose-registration-failure": "TOOL::diagnose_registration_failure",
    "diagnose-incoming-call-failure": "TOOL::diagnose_incoming_call_failure",
    "diagnose-answer-failure": "TOOL::diagnose_answer_failure",
    "diagnose-one-way-audio": "TOOL::diagnose_one_way_audio",
    "tool-open-app-observation": "TOOL::open_app",
    "tool-login-agent-observation": "TOOL::login_agent",
    "tool-wait-for-ready-observation": "TOOL::wait_for_ready",
    "tool-list-sessions-observation": "TOOL::list_sessions",
    "tool-close-session-observation": "TOOL::close_session",
    "tool-reset-session-observation": "TOOL::reset_session",
    "tool-get-registration-status-observation": "TOOL::get_registration_status",
    "tool-assert-registered-observation": "TOOL::assert_registered",
    "tool-hangup-call-observation": "TOOL::hangup_call",
    "tool-get-ui-call-state-observation": "TOOL::get_ui_call_state",
    "tool-get-active-session-snapshot-observation": "TOOL::get_active_session_snapshot",
    "tool-get-store-snapshot-observation": "TOOL::get_store_snapshot",
    "tool-get-peer-connection-summary-observation": "TOOL::get_peer_connection_summary",
    "tool-get-webrtc-stats-observation": "TOOL::get_webrtc_stats",
    "tool-get-environment-snapshot-observation": "TOOL::get_environment_snapshot",
    "tool-screenshot-observation": "TOOL::screenshot",
    "protocol-initialize-discovery-observation": "PROTOCOL::initialize_and_discovery",
}


def enrich_validation(
    *,
    contract_matrix_path: str | Path,
    validation_summary_path: str | Path,
    ingested_bundles: list[BundleIngestion],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract_rows = json.loads(Path(contract_matrix_path).read_text(encoding="utf-8"))
    validation_summary = json.loads(Path(validation_summary_path).read_text(encoding="utf-8"))

    by_contract: dict[str, BundleIngestion] = {}
    for bundle in ingested_bundles:
        contract_id = SCENARIO_TO_CONTRACT.get(bundle.scenario_id)
        if contract_id:
            by_contract[contract_id] = bundle

    mapping_rows: list[dict[str, Any]] = []
    enriched_rows: list[dict[str, Any]] = []
    root_cause_counter: Counter[str] = Counter()
    root_cause_contracts: dict[str, set[str]] = defaultdict(set)
    root_cause_scenarios: dict[str, set[str]] = defaultdict(set)

    for row in contract_rows:
        contract_id = row.get("contract_id", "")
        bundle = by_contract.get(contract_id)
        if bundle is None:
            mapping_rows.append(
                {
                    "contract_id": contract_id,
                    "scenario_id": None,
                    "bundle_path": None,
                    "manifest_path": None,
                    "linkage_status": "missing",
                }
            )
            enriched_rows.append(
                {
                    **row,
                    "bundle_path": None,
                    "manifest_path": None,
                    "primary_root_cause": "diagnostics_collection_gap",
                    "supporting_signals": [],
                    "collection_gaps": ["no linked diagnostics bundle"],
                }
            )
            continue

        root_cause = classify_root_cause(bundle)
        root_cause_counter[root_cause] += 1
        root_cause_contracts[root_cause].add(contract_id)
        root_cause_scenarios[root_cause].add(bundle.scenario_id)
        mapping_rows.append(
            {
                "contract_id": contract_id,
                "scenario_id": bundle.scenario_id,
                "bundle_path": bundle.bundle_path,
                "manifest_path": bundle.manifest_path,
                "linkage_status": "linked",
                "run_id": Path(bundle.manifest_path).parts[-4] if bundle.manifest_path else None,
            }
        )
        enriched_rows.append(
            {
                **row,
                "bundle_path": bundle.bundle_path,
                "manifest_path": bundle.manifest_path,
                "primary_root_cause": root_cause,
                "supporting_signals": bundle.signals_present,
                "collection_gaps": bundle.collection_gaps,
                "bundle_health": bundle.bundle_health,
                "bundle_status": bundle.status,
                "bundle_failure_classification": bundle.failure_classification,
            }
        )

    total_rows = len(enriched_rows)
    linked_rows = sum(1 for item in mapping_rows if item["linkage_status"] == "linked")
    diagnostics_coverage_score = round((linked_rows / total_rows) * 100, 2) if total_rows else 0.0

    status_counter = Counter(str(item.get("validation_status", "INCONCLUSIVE")) for item in contract_rows)
    enriched_summary = {
        "timestamp": validation_summary.get("timestamp"),
        "source_validation_summary": str(validation_summary_path),
        "total_pass": status_counter.get("PASS", 0),
        "total_fail": status_counter.get("FAIL", 0),
        "total_partial": status_counter.get("PARTIAL", 0),
        "total_inconclusive": status_counter.get("INCONCLUSIVE", 0),
        "diagnostics_coverage_score": diagnostics_coverage_score,
        "linked_contracts": linked_rows,
        "total_contracts": total_rows,
    }

    root_cause_summary = {
        "categories": [
            {
                "category": category,
                "count": count,
                "scenarios": sorted(root_cause_scenarios[category]),
                "contracts": sorted(root_cause_contracts[category]),
            }
            for category, count in sorted(root_cause_counter.items(), key=lambda item: (-item[1], item[0]))
        ]
    }

    contract_to_bundle_map = {
        "source_contract_matrix": str(contract_matrix_path),
        "entries": mapping_rows,
    }

    return contract_to_bundle_map, root_cause_summary, {
        **enriched_summary,
        "enriched_contracts": enriched_rows,
    }
