#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-prioritize remediation batches from signatures")
    parser.add_argument(
        "--signatures-dir",
        default="docs/failure-signatures/telecom-ui",
    )
    parser.add_argument(
        "--validation-dir",
        default="docs/validation/telecom-browser-mcp-v0.2",
    )
    parser.add_argument(
        "--validation-diagnostics-dir",
        default="docs/validation/telecom-browser-mcp-v0.2-diagnostics",
    )
    parser.add_argument(
        "--remediation-dir",
        default="docs/remediation/telecom-browser-mcp-v0.2",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/prioritization/telecom-browser-mcp",
    )
    return parser.parse_args()


def _latest(path: Path, pattern: str) -> Path:
    matches = sorted(path.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"missing {pattern} under {path}")
    return matches[-1]


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_previous_signature_library(signatures_dir: Path, current_path: Path) -> list[dict[str, Any]]:
    all_libs = sorted(signatures_dir.glob("*--failure-signatures.json"))
    if len(all_libs) < 2:
        return []
    prev = all_libs[-2] if all_libs[-1] == current_path else all_libs[-1]
    return _load(prev)


def main() -> int:
    from telecom_browser_mcp.failure_priority_scorer import classify_domain, score_signatures
    from telecom_browser_mcp.remediation_batch_recommender import recommend_batches
    from telecom_browser_mcp.signature_regression_detector import classify_known_vs_new

    args = _parse_args()
    signatures_dir = Path(args.signatures_dir)
    base_validation_dir = Path(args.validation_dir)
    validation_dir = Path(args.validation_diagnostics_dir)
    remediation_dir = Path(args.remediation_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    current_signatures_path = _latest(signatures_dir, "*--failure-signatures.json")
    signature_summary_path = _latest(signatures_dir, "*--signature-summary.json")
    signature_frequency_path = _latest(signatures_dir, "*--signature-frequency-report.json")
    signature_map_path = _latest(signatures_dir, "*--signature-to-contract-map.json")

    signatures = _load(current_signatures_path)
    _ = _load(signature_summary_path)
    _ = _load(signature_frequency_path)
    _ = _load(signature_map_path)
    base_validation_summary_path = _latest(base_validation_dir, "*--validation-summary.json")
    base_scenario_results_path = _latest(base_validation_dir, "*--scenario-results.json")
    _ = _load(base_validation_summary_path)
    _ = _load(base_scenario_results_path)
    _ = _load(validation_dir / "enriched-validation-summary.json")
    _ = _load(validation_dir / "root-cause-summary.json")
    _ = _load(validation_dir / "contract-to-bundle-map.json")

    previous_signatures = _read_previous_signature_library(signatures_dir, current_signatures_path)
    regression_rows = classify_known_vs_new(signatures, previous_signatures)
    novelty_by_id = {row.signature_id: row.classification for row in regression_rows}
    ranked = score_signatures(signatures, novelty_by_id)
    batches = recommend_batches(ranked)

    new_regressions = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": [
            row.to_dict()
            for row in regression_rows
            if row.classification in {"new_signature", "known_but_regressing", "unknown_unmatched"}
        ],
    }

    ranking_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ranked_signatures": ranked,
    }
    batches_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommended_batches": batches,
    }
    priority_counts = Counter(item["priority_bucket"] for item in ranked)
    domain_counts = Counter(classify_domain(sig) for sig in signatures)
    novelty_counts = Counter(row.classification for row in regression_rows)

    readiness_checks = {
        "failure_signatures": current_signatures_path.exists(),
        "signature_summary": signature_summary_path.exists(),
        "signature_frequency_report": signature_frequency_path.exists(),
        "signature_to_contract_map": signature_map_path.exists(),
        "base_validation_summary": base_validation_summary_path.exists(),
        "base_scenario_results": base_scenario_results_path.exists(),
        "enriched_validation_summary": (validation_dir / "enriched-validation-summary.json").exists(),
        "root_cause_summary": (validation_dir / "root-cause-summary.json").exists(),
        "contract_to_bundle_map": (validation_dir / "contract-to-bundle-map.json").exists(),
        "remediation_history_present": bool(list(remediation_dir.glob("*--rerun-summary.json"))),
    }

    priority_summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_failures_analyzed": sum(item.get("occurrence_count", 0) for item in signatures),
        "total_signatures": len(signatures),
        "new_vs_known": dict(novelty_counts),
        "priority_bucket_counts": dict(priority_counts),
        "domain_distribution": dict(domain_counts),
        "recommended_batch_count": len(batches),
    }

    _write(output_dir / f"{ts}--priority-summary.json", priority_summary)
    _write(output_dir / f"{ts}--recommended-batches.json", batches_payload)
    _write(output_dir / f"{ts}--signature-priority-ranking.json", ranking_payload)
    _write(output_dir / f"{ts}--new-regressions.json", new_regressions)

    _write_docs(
        output_dir=output_dir,
        ts=ts,
        readiness_checks=readiness_checks,
        ranked=ranked,
        batches=batches,
        novelty_counts=novelty_counts,
        domain_counts=domain_counts,
        priority_summary=priority_summary,
        source_paths={
            "current_signatures": str(current_signatures_path),
            "signature_summary": str(signature_summary_path),
            "signature_frequency": str(signature_frequency_path),
            "signature_map": str(signature_map_path),
            "base_validation_summary": str(base_validation_summary_path),
            "base_scenario_results": str(base_scenario_results_path),
            "enriched_summary": str(validation_dir / "enriched-validation-summary.json"),
            "root_cause_summary": str(validation_dir / "root-cause-summary.json"),
            "contract_to_bundle": str(validation_dir / "contract-to-bundle-map.json"),
        },
    )

    sys.stderr.write(f"[prioritize_remediation_batches] wrote outputs to {output_dir}\n")
    return 0


def _write_docs(
    *,
    output_dir: Path,
    ts: str,
    readiness_checks: dict[str, bool],
    ranked: list[dict[str, Any]],
    batches: list[dict[str, Any]],
    novelty_counts: Counter,
    domain_counts: Counter,
    priority_summary: dict[str, Any],
    source_paths: dict[str, str],
) -> None:
    top = ranked[:5]
    lines_map = {
        f"{ts}--prioritization-plan.md": [
            "# Prioritization Plan",
            "",
            f"- timestamp: {ts}",
            *[f"- {k}: `{v}`" for k, v in source_paths.items()],
            "",
            "1. Check input readiness and schema health.",
            "2. Detect known/new/regressing signatures.",
            "3. Score and bucket signatures by risk model.",
            "4. Recommend advisory remediation batches.",
        ],
        f"{ts}--input-readiness-check.md": [
            "# Input Readiness Check",
            "",
            *[f"- {k}: {'PASS' if ok else 'FAIL'}" for k, ok in readiness_checks.items()],
        ],
        f"{ts}--priority-model.md": [
            "# Priority Model",
            "",
            "- factors: novelty, severity, frequency, contract impact, trend, confidence, diagnostics quality, domain",
            "- buckets: P0/P1/P2/P3/P4",
            "- domain override: environment_or_ci maps to P4 noise bucket",
        ],
        f"{ts}--signature-risk-ranking.md": [
            "# Signature Risk Ranking",
            "",
            *[
                f"- `{item['signature_id']}` {item['signature_name']} "
                f"score={item['score']} bucket={item['priority_bucket']} domain={item['domain']}"
                for item in top
            ],
        ],
        f"{ts}--batch-recommendations.md": [
            "# Batch Recommendations",
            "",
            *[
                f"- `{batch['batch_id']}` {batch['priority_bucket']} {batch['domain']} "
                f"signatures={batch['signature_count']}"
                for batch in batches
            ],
        ],
        f"{ts}--environment-vs-product-analysis.md": [
            "# Environment vs Product Analysis",
            "",
            f"- product_logic: {domain_counts.get('product_logic', 0)}",
            f"- browser_lifecycle_or_harness: {domain_counts.get('browser_lifecycle_or_harness', 0)}",
            f"- diagnostics_pipeline: {domain_counts.get('diagnostics_pipeline', 0)}",
            f"- environment_or_ci: {domain_counts.get('environment_or_ci', 0)}",
            f"- contract_definition: {domain_counts.get('contract_definition', 0)}",
        ],
        f"{ts}--new-vs-known-failure-analysis.md": [
            "# New vs Known Failure Analysis",
            "",
            f"- known_signature: {novelty_counts.get('known_signature', 0)}",
            f"- known_but_regressing: {novelty_counts.get('known_but_regressing', 0)}",
            f"- new_signature: {novelty_counts.get('new_signature', 0)}",
            f"- unknown_unmatched: {novelty_counts.get('unknown_unmatched', 0)}",
        ],
        f"{ts}--first-prioritized-run.md": [
            "# First Prioritized Run",
            "",
            "## Executive Summary",
            f"- total failures analyzed: {priority_summary['total_failures_analyzed']}",
            f"- total signatures: {priority_summary['total_signatures']}",
            "",
            "## Top Remediation Candidates",
            *[
                f"- {item['signature_name']} ({item['priority_bucket']}, score={item['score']})"
                for item in top
            ],
            "",
            "## New Regressions",
            f"- count: {novelty_counts.get('new_signature', 0) + novelty_counts.get('known_but_regressing', 0)}",
            "",
            "## Known Stable Failures",
            f"- count: {novelty_counts.get('known_signature', 0)}",
            "",
            "## Environment Noise",
            f"- count: {domain_counts.get('environment_or_ci', 0)}",
            "",
            "## Suggested Next Pipelines",
            "- remediate product_logic P0/P1 signatures",
            "- route diagnostics_pipeline items to diagnostics-hardening pipeline",
            "- keep environment_or_ci items in infra triage queue",
        ],
        f"{ts}--remaining-gaps.md": [
            "# Remaining Gaps",
            "",
            "- trend direction currently relies on previous signature snapshot only",
            "- no time-windowed historical frequency model yet",
            "- contract-definition vs product logic ambiguity still heuristic",
        ],
    }
    for name, lines in lines_map.items():
        (output_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
