#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Integrate browser diagnostics bundles into v0.2 contract validation evidence"
    )
    parser.add_argument(
        "--validation-dir",
        default="docs/validation/telecom-browser-mcp-v0.2",
    )
    parser.add_argument(
        "--lifecycle-results",
        default=None,
        help="Path to lifecycle-fault-results.json. Defaults to latest diagnostics lifecycle run.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/validation/telecom-browser-mcp-v0.2-diagnostics",
    )
    return parser.parse_args()


def _latest_file(directory: Path, pattern: str) -> Path:
    candidates = sorted(directory.glob(pattern))
    if not candidates:
        raise FileNotFoundError(f"no files matching {pattern} in {directory}")
    return candidates[-1]


def _find_latest_lifecycle_results() -> Path:
    root = Path("docs/harness/browser-diagnostics-wiring")
    candidates = sorted(root.glob("*-lifecycle-run/lifecycle-fault-results.json"))
    if not candidates:
        raise FileNotFoundError("no lifecycle diagnostics run outputs found")
    return candidates[-1]


def _write_markdown(
    output_dir: Path,
    timestamp: str,
    *,
    integration_plan: dict,
    mapping_summary: dict,
    ingestion_summary: dict,
    classification_rules: list[str],
    reporting_upgrade: dict,
    first_run: dict,
    remaining_gaps: list[str],
) -> None:
    files = {
        f"{timestamp}--integration-plan.md": [
            "# Integration Plan",
            "",
            f"- timestamp: {timestamp}",
            f"- validation_summary: `{integration_plan['validation_summary']}`",
            f"- lifecycle_results: `{integration_plan['lifecycle_results']}`",
            "",
            "## Steps",
            "1. Ingest lifecycle diagnostics manifests.",
            "2. Link contracts to scenario bundles by scenario_id mapping.",
            "3. Classify root causes from bundle health/signals.",
            "4. Write enriched machine-readable summaries.",
        ],
        f"{timestamp}--diagnostics-to-contract-mapping.md": [
            "# Diagnostics to Contract Mapping",
            "",
            f"- linked_contracts: {mapping_summary['linked_contracts']}",
            f"- total_contracts: {mapping_summary['total_contracts']}",
            f"- linkage_coverage_percent: {mapping_summary['coverage']}",
            "",
            "## Primary key",
            "- `scenario_id`",
            "",
            "## Fallback strategy",
            "- timestamp window + session_id + tool name (not needed in this run).",
        ],
        f"{timestamp}--artifact-ingestion-design.md": [
            "# Artifact Ingestion Design",
            "",
            f"- ingested_bundles: {ingestion_summary['ingested_bundles']}",
            f"- bundle_health: {json.dumps(ingestion_summary['bundle_health'])}",
            "",
            "## Normalized fields",
            "- scenario_id",
            "- bundle_path",
            "- signals_present",
            "- signals_missing",
            "- collection_gaps",
            "- cleanup_status",
        ],
        f"{timestamp}--root-cause-classification-rules.md": [
            "# Root Cause Classification Rules",
            "",
            "Ordered rules:",
            *[f"- {rule}" for rule in classification_rules],
        ],
        f"{timestamp}--validation-reporting-upgrade.md": [
            "# Validation Reporting Upgrade",
            "",
            f"- enriched_contract_rows: {reporting_upgrade['enriched_contract_rows']}",
            f"- diagnostics_coverage_score: {reporting_upgrade['diagnostics_coverage_score']}",
            "",
            "Added fields per contract row:",
            "- bundle_path",
            "- manifest_path",
            "- primary_root_cause",
            "- supporting_signals",
            "- collection_gaps",
            "- bundle_health",
        ],
        f"{timestamp}--first-integrated-run.md": [
            "# First Integrated Run",
            "",
            f"- timestamp: {timestamp}",
            f"- ingested_bundles: {first_run['ingested_bundles']}",
            f"- linked_contracts: {first_run['linked_contracts']}",
            f"- diagnostics_coverage_score: {first_run['diagnostics_coverage_score']}",
            "",
            "Outputs:",
            "- `contract-to-bundle-map.json`",
            "- `root-cause-summary.json`",
            "- `enriched-validation-summary.json`",
        ],
        f"{timestamp}--remaining-gaps.md": [
            "# Remaining Gaps",
            "",
            *[f"- {gap}" for gap in remaining_gaps],
        ],
    }
    for name, lines in files.items():
        (output_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    from telecom_browser_mcp.validation.validation_diagnostics_ingestor import (
        ingest_lifecycle_results,
    )
    from telecom_browser_mcp.validation.validation_report_enricher import enrich_validation

    args = _parse_args()
    validation_dir = Path(args.validation_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    validation_summary_path = _latest_file(validation_dir, "*--validation-summary.json")
    contract_matrix_path = _latest_file(validation_dir, "*--contract-matrix.json")
    lifecycle_results_path = Path(args.lifecycle_results) if args.lifecycle_results else _find_latest_lifecycle_results()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    ingested = ingest_lifecycle_results(lifecycle_results_path)
    contract_to_bundle_map, root_cause_summary, enriched = enrich_validation(
        contract_matrix_path=contract_matrix_path,
        validation_summary_path=validation_summary_path,
        ingested_bundles=ingested,
    )

    (output_dir / "contract-to-bundle-map.json").write_text(
        json.dumps(contract_to_bundle_map, indent=2),
        encoding="utf-8",
    )
    (output_dir / "root-cause-summary.json").write_text(
        json.dumps(root_cause_summary, indent=2),
        encoding="utf-8",
    )
    (output_dir / "enriched-validation-summary.json").write_text(
        json.dumps(enriched, indent=2),
        encoding="utf-8",
    )

    linked_contracts = sum(
        1 for row in contract_to_bundle_map["entries"] if row["linkage_status"] == "linked"
    )
    total_contracts = len(contract_to_bundle_map["entries"])
    bundle_health: dict[str, int] = {}
    for item in ingested:
        bundle_health[item.bundle_health] = bundle_health.get(item.bundle_health, 0) + 1

    _write_markdown(
        output_dir,
        timestamp,
        integration_plan={
            "validation_summary": str(validation_summary_path),
            "lifecycle_results": str(lifecycle_results_path),
        },
        mapping_summary={
            "linked_contracts": linked_contracts,
            "total_contracts": total_contracts,
            "coverage": round((linked_contracts / total_contracts) * 100, 2) if total_contracts else 0.0,
        },
        ingestion_summary={
            "ingested_bundles": len(ingested),
            "bundle_health": bundle_health,
        },
        classification_rules=[
            "missing/malformed bundle -> diagnostics_collection_gap",
            "scenario_id contains stale_selector -> selector_stale_or_dom_drift",
            "scenario_id contains page_detach/page_closed -> page_closed_or_detached",
            "scenario_id contains context_closure -> context_invalidated",
            "scenario_id contains browser_crash -> browser_unavailable",
            "page_errors present -> javascript_runtime_error",
            "network failures present -> network_failure",
            "collection_gaps present -> diagnostics_collection_gap",
            "unknown classification -> contract_ambiguous/unknown",
        ],
        reporting_upgrade={
            "enriched_contract_rows": len(enriched.get("enriched_contracts", [])),
            "diagnostics_coverage_score": enriched.get("diagnostics_coverage_score", 0.0),
        },
        first_run={
            "ingested_bundles": len(ingested),
            "linked_contracts": linked_contracts,
            "diagnostics_coverage_score": enriched.get("diagnostics_coverage_score", 0.0),
        },
        remaining_gaps=[
            "Most non-lifecycle contracts have no direct diagnostics bundle mapping yet.",
            "Lifecycle bundles from synthetic harness are often partial by design (no live page/context).",
            "Fallback mapping using timestamp/session/tool is not exercised in this run.",
        ],
    )

    sys.stderr.write(
        f"[validate_v0_2_contracts] wrote diagnostics integration outputs to {output_dir}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
