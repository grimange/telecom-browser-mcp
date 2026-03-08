from __future__ import annotations

import json
from pathlib import Path

from telecom_browser_mcp.validation.validation_diagnostics_ingestor import BundleIngestion
from telecom_browser_mcp.validation.validation_report_enricher import enrich_validation


def test_enrichment_links_lifecycle_contracts(tmp_path: Path) -> None:
    contract_matrix = tmp_path / "contract-matrix.json"
    contract_matrix.write_text(
        json.dumps(
            [
                {"contract_id": "LIFECYCLE::crash_recovery", "validation_status": "PASS"},
                {"contract_id": "TOOL::open_app", "validation_status": "PASS"},
            ]
        ),
        encoding="utf-8",
    )
    validation_summary = tmp_path / "validation-summary.json"
    validation_summary.write_text(json.dumps({"timestamp": "20260307T000000Z"}), encoding="utf-8")

    ingested = [
        BundleIngestion(
            scenario_id="browser_crash_recovery",
            bundle_path="/tmp/bundle",
            manifest_path="/tmp/bundle/manifest.json",
            signals_present=["console"],
            signals_missing=["trace"],
            collection_gaps=["trace unavailable"],
            cleanup_status="unknown",
            bundle_health="partial",
            failure_classification="session",
            status="failed",
        )
    ]

    mapping, root_cause, enriched = enrich_validation(
        contract_matrix_path=contract_matrix,
        validation_summary_path=validation_summary,
        ingested_bundles=ingested,
    )

    linked = [x for x in mapping["entries"] if x["linkage_status"] == "linked"]
    assert len(linked) == 1
    assert linked[0]["contract_id"] == "LIFECYCLE::crash_recovery"
    assert root_cause["categories"]
    assert "diagnostics_coverage_score" in enriched


def test_enrichment_links_tool_contracts_from_runtime_scenarios(tmp_path: Path) -> None:
    contract_matrix = tmp_path / "contract-matrix.json"
    contract_matrix.write_text(
        json.dumps(
            [
                {"contract_id": "TOOL::collect_browser_logs", "validation_status": "PASS"},
                {"contract_id": "TOOL::collect_debug_bundle", "validation_status": "PASS"},
                {"contract_id": "TOOL::open_app", "validation_status": "PASS"},
            ]
        ),
        encoding="utf-8",
    )
    validation_summary = tmp_path / "validation-summary.json"
    validation_summary.write_text(json.dumps({"timestamp": "20260307T000000Z"}), encoding="utf-8")

    ingested = [
        BundleIngestion(
            scenario_id="collect-browser-logs",
            bundle_path="/tmp/run/collect-browser-logs",
            manifest_path="/tmp/run/collect-browser-logs/manifest.json",
            signals_present=["console", "network"],
            signals_missing=["trace"],
            collection_gaps=["trace unavailable"],
            cleanup_status="unknown",
            bundle_health="partial",
            failure_classification="diagnostic",
            status="ok",
        ),
        BundleIngestion(
            scenario_id="collect-debug-bundle",
            bundle_path="/tmp/run/collect-debug-bundle",
            manifest_path="/tmp/run/collect-debug-bundle/manifest.json",
            signals_present=["console", "network"],
            signals_missing=["trace"],
            collection_gaps=["trace unavailable"],
            cleanup_status="unknown",
            bundle_health="partial",
            failure_classification="diagnostic",
            status="ok",
        ),
        BundleIngestion(
            scenario_id="tool-open-app-observation",
            bundle_path="/tmp/run/tool-open-app-observation",
            manifest_path="/tmp/run/tool-open-app-observation/manifest.json",
            signals_present=["console"],
            signals_missing=["trace"],
            collection_gaps=["trace unavailable"],
            cleanup_status="unknown",
            bundle_health="partial",
            failure_classification="diagnostic",
            status="ok",
        ),
    ]

    mapping, _root_cause, enriched = enrich_validation(
        contract_matrix_path=contract_matrix,
        validation_summary_path=validation_summary,
        ingested_bundles=ingested,
    )

    linked = [x for x in mapping["entries"] if x["linkage_status"] == "linked"]
    assert len(linked) == 3
    assert {x["contract_id"] for x in linked} == {
        "TOOL::collect_browser_logs",
        "TOOL::collect_debug_bundle",
        "TOOL::open_app",
    }
    assert enriched["diagnostics_coverage_score"] == 100.0
