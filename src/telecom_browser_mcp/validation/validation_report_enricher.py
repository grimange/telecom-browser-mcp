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
