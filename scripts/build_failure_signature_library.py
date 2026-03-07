#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build telecom UI failure signature library")
    parser.add_argument(
        "--validation-diagnostics-dir",
        default="docs/validation/telecom-browser-mcp-v0.2-diagnostics",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/failure-signatures/telecom-ui",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_path_from_manifest(manifest_path: str | None) -> dict[str, Any] | None:
    if not manifest_path:
        return None
    path = Path(manifest_path)
    if not path.exists():
        return None
    return _load_json(path)


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_docs(
    output_dir: Path,
    ts: str,
    *,
    library: list[dict[str, Any]],
    summary: dict[str, Any],
    signature_to_contract: dict[str, Any],
    frequency: dict[str, Any],
) -> None:
    docs = {
        f"{ts}--signature-library-design.md": [
            "# Signature Library Design",
            "",
            "- rule-based extraction from enriched validation and diagnostics manifests",
            "- deterministic normalization before signature extraction",
            "- explicit confidence and recommended remediation actions",
        ],
        f"{ts}--signal-normalization-rules.md": [
            "# Signal Normalization Rules",
            "",
            "- root cause + bundle health + collection gaps -> diagnostics_gap_present",
            "- root cause selector_stale_or_dom_drift -> selector/DOM drift feature",
            "- root cause page_closed_or_detached -> page_closed_before_action",
            "- root cause context_invalidated -> context_closed_during_wait",
            "- manifest trace/screenshot presence -> availability features",
        ],
        f"{ts}--signature-extraction-rules.md": [
            "# Signature Extraction Rules",
            "",
            "- selector_stale_after_dom_refresh",
            "- page_closed_before_action",
            "- javascript_runtime_error",
            "- network_failure_ui_timeout",
            "- diagnostics_bundle_missing_on_failure",
        ],
        f"{ts}--clustering-and-dedup-strategy.md": [
            "# Clustering and Dedup Strategy",
            "",
            "- dedup key: (signature_name, category)",
            "- aggregate occurrence_count, contracts, tools, representative scenarios",
            "- keep first representative evidence and merge frequency counts",
        ],
        f"{ts}--signature-schema.md": [
            "# Signature Schema",
            "",
            "- signature_id, version, name, category, description",
            "- matching_rules, supporting_evidence_shape, recommended_actions",
            "- representative_examples, contract_ids, tool_names, occurrence_count",
            "- confidence_notes, created_at, updated_at",
        ],
        f"{ts}--review-and-curation-workflow.md": [
            "# Review and Curation Workflow",
            "",
            "1. extract candidate signatures",
            "2. deduplicate by rule key",
            "3. render report",
            "4. curate (merge/rename/promote/reject/environment-only)",
        ],
        f"{ts}--first-signature-build.md": [
            "# First Signature Build",
            "",
            f"- total signatures: {summary['total_signatures']}",
            f"- total occurrences: {summary['total_occurrences']}",
            f"- top categories: {', '.join(summary['top_categories']) if summary['top_categories'] else 'none'}",
            "",
            "## Signature Quality",
            f"- high-confidence signatures: {summary['high_confidence_signatures']}",
            "",
            "## Product vs Environment Failures",
            f"- product signatures: {summary['product_signatures']}",
            f"- environment signatures: {summary['environment_signatures']}",
            "",
            "## Diagnostics Gaps",
            f"- diagnostics gap signatures: {summary['diagnostics_gap_signatures']}",
        ],
        f"{ts}--remaining-gaps.md": [
            "# Remaining Gaps",
            "",
            "- signature extraction currently uses deterministic rule families only",
            "- telecom call-state race signatures are not modeled yet",
            "- webrtc readiness and registration race signatures are not modeled yet",
            "- linkage is strongest for lifecycle contracts; non-lifecycle mapping remains sparse",
        ],
    }
    for name, lines in docs.items():
        (output_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ensure_baseline_signature_families(library: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required = [
        ("selector_stale_after_dom_refresh", "selector_stale_after_dom_refresh"),
        ("page_closed_before_action", "page_closed_before_action"),
        ("javascript_runtime_error", "javascript_runtime_error"),
        ("network_failure_ui_timeout", "network_failure_ui_timeout"),
        ("diagnostics_bundle_missing_on_failure", "diagnostics_bundle_missing_on_failure"),
    ]
    present = {(item["name"], item["category"]) for item in library}
    next_id = len(library) + 1
    now = datetime.now(timezone.utc).isoformat()
    for name, category in required:
        if (name, category) in present:
            continue
        library.append(
            {
                "signature_id": f"SIG-{next_id:03d}",
                "version": "v1",
                "name": name,
                "category": category,
                "description": f"Baseline signature family template for {name}",
                "matching_rules": [],
                "supporting_evidence_shape": [
                    "manifest.json",
                    "console.json",
                    "network.json",
                    "page-errors.json",
                ],
                "recommended_actions": ["collect additional evidence", "confirm rule triggers on next run"],
                "representative_examples": [],
                "contract_ids": [],
                "tool_names": [],
                "occurrence_count": 0,
                "confidence_notes": "weak",
                "created_at": now,
                "updated_at": now,
                "trigger_signals": [],
                "supporting_signals": [],
                "common_root_cause": "unknown",
                "affected_contract_ids": [],
                "representative_scenarios": [],
                "recommended_actions_v1": ["collect additional evidence"],
            }
        )
        next_id += 1
    return library


def main() -> int:
    from telecom_browser_mcp.failure_signature_extractor import extract_signature_candidates
    from telecom_browser_mcp.signature_library_store import build_signature_library
    from telecom_browser_mcp.signature_signal_normalizer import normalize_failure_signals

    args = _parse_args()
    validation_dir = Path(args.validation_diagnostics_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    enriched = _load_json(validation_dir / "enriched-validation-summary.json")
    mapping = _load_json(validation_dir / "contract-to-bundle-map.json")
    _ = _load_json(validation_dir / "root-cause-summary.json")

    manifest_by_contract: dict[str, dict[str, Any]] = {}
    for entry in mapping.get("entries", []):
        contract_id = entry.get("contract_id")
        manifest = _artifact_path_from_manifest(entry.get("manifest_path"))
        if contract_id and manifest is not None:
            manifest_by_contract[str(contract_id)] = manifest

    normalized = normalize_failure_signals(enriched.get("enriched_contracts", []), manifest_by_contract)
    candidates = extract_signature_candidates(normalized)
    library = _ensure_baseline_signature_families(build_signature_library(candidates))

    signature_to_contract: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": [
            {
                "signature_id": item["signature_id"],
                "signature_name": item["name"],
                "contract_ids": item["contract_ids"],
                "tool_names": item["tool_names"],
            }
            for item in library
        ],
    }

    category_counts = Counter(item["category"] for item in library)
    by_contract = defaultdict(list)
    by_tool = defaultdict(list)
    for item in library:
        for cid in item["contract_ids"]:
            by_contract[cid].append(item["signature_id"])
        for tool in item["tool_names"]:
            by_tool[tool].append(item["signature_id"])

    frequency = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_signatures": len(library),
        "signature_occurrences": [
            {
                "signature_id": item["signature_id"],
                "name": item["name"],
                "occurrence_count": item["occurrence_count"],
                "category": item["category"],
            }
            for item in library
        ],
        "by_category": dict(category_counts),
        "by_contract": {k: sorted(set(v)) for k, v in by_contract.items()},
        "by_tool": {k: sorted(set(v)) for k, v in by_tool.items()},
    }

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_signatures": len(library),
        "total_occurrences": sum(item["occurrence_count"] for item in library),
        "top_categories": [key for key, _ in category_counts.most_common(3)],
        "high_confidence_signatures": sum(
            1 for item in library if item.get("confidence_notes") in {"exact", "strong"}
        ),
        "product_signatures": sum(
            1
            for item in library
            if item["category"]
            not in {"environment_blocked_execution", "diagnostics_bundle_missing_on_failure"}
        ),
        "environment_signatures": sum(
            1 for item in library if item["category"] == "environment_blocked_execution"
        ),
        "diagnostics_gap_signatures": sum(
            1 for item in library if item["category"] == "diagnostics_bundle_missing_on_failure"
        ),
    }

    _write(output_dir / f"{ts}--failure-signatures.json", library)
    _write(output_dir / f"{ts}--signature-summary.json", summary)
    _write(output_dir / f"{ts}--signature-to-contract-map.json", signature_to_contract)
    _write(output_dir / f"{ts}--signature-frequency-report.json", frequency)
    _write_docs(
        output_dir,
        ts,
        library=library,
        summary=summary,
        signature_to_contract=signature_to_contract,
        frequency=frequency,
    )

    sys.stderr.write(f"[build_failure_signature_library] wrote outputs to {output_dir}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
