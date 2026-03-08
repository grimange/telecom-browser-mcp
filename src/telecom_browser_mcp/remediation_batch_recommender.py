from __future__ import annotations

from collections import defaultdict
from typing import Any


def recommend_batches(ranked_signatures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in ranked_signatures:
        if int(item.get("occurrence_count", 0)) <= 0:
            # Ignore template-only signatures that have not been observed in evidence.
            continue
        grouped[(item["priority_bucket"], item["domain"])].append(item)

    batches: list[dict[str, Any]] = []
    index = 1
    for (bucket, domain), rows in sorted(grouped.items(), key=_group_sort_key):
        target_signature_ids = [str(r["signature_id"]) for r in rows]
        impacted_contracts: set[str] = set()
        for r in rows:
            impacted_contracts.update(r.get("contract_ids", []))
        batches.append(
            {
                "batch_id": f"RB-{index:03d}",
                "priority_bucket": bucket,
                "domain": domain,
                "target_signature_ids": target_signature_ids,
                "impacted_contracts": sorted(impacted_contracts),
                "problem_statement": _problem_statement(domain),
                "recommended_investigation_areas": _investigation_areas(domain),
                "signature_count": len(rows),
            }
        )
        index += 1
    return batches


def _group_sort_key(item: tuple[tuple[str, str], list[dict[str, Any]]]) -> tuple[int, str]:
    (bucket, domain), _rows = item
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    return (order.get(bucket, 9), domain)


def _problem_statement(domain: str) -> str:
    mapping = {
        "product_logic": "Recurring product logic failures need focused remediation.",
        "browser_lifecycle_or_harness": "Lifecycle/harness reliability issues impact deterministic validation.",
        "diagnostics_pipeline": "Diagnostics gaps prevent strong root-cause evidence.",
        "environment_or_ci": "Environment instability should be isolated from product regressions.",
        "contract_definition": "Contract mapping ambiguity needs clarification before remediation.",
    }
    return mapping.get(domain, "Mixed failure set requiring triage.")


def _investigation_areas(domain: str) -> list[str]:
    mapping = {
        "product_logic": ["tools/orchestrator", "adapter runtime state transitions", "ui/action sequencing"],
        "browser_lifecycle_or_harness": ["session manager", "fault injection hooks", "parallel isolation"],
        "diagnostics_pipeline": ["browser diagnostics collector", "bundle manifest coverage", "signal linkage"],
        "environment_or_ci": ["interop probe runtime", "sandbox/browser prerequisites", "network reachability"],
        "contract_definition": ["contract matrix rules", "validation method alignment"],
    }
    return mapping.get(domain, ["triage logs", "validation artifacts"])
