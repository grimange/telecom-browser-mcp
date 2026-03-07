from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any


def build_signature_library(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        key = (candidate["signature_name"], candidate["category"])
        grouped[key].append(candidate)

    now = datetime.now(timezone.utc).isoformat()
    library: list[dict[str, Any]] = []
    for idx, ((name, category), rows) in enumerate(sorted(grouped.items()), start=1):
        contract_ids = sorted({str(r.get("contract_id")) for r in rows if r.get("contract_id")})
        tools = sorted({str(r.get("tool_name")) for r in rows if r.get("tool_name")})
        representative = rows[0]
        library.append(
            {
                "signature_id": f"SIG-{idx:03d}",
                "version": "v1",
                "name": name,
                "category": category,
                "description": f"Detected recurring telecom UI failure pattern: {name}",
                "matching_rules": representative.get("trigger_signals", []),
                "supporting_evidence_shape": [
                    "manifest.json",
                    "console.json",
                    "network.json",
                    "page-errors.json",
                ],
                "recommended_actions": representative.get("recommended_actions", []),
                "representative_examples": [
                    {
                        "contract_id": representative.get("contract_id"),
                        "scenario": representative.get("representative_scenario"),
                    }
                ],
                "contract_ids": contract_ids,
                "tool_names": tools,
                "occurrence_count": len(rows),
                "confidence_notes": representative.get("confidence_model", "weak"),
                "created_at": now,
                "updated_at": now,
                "trigger_signals": representative.get("trigger_signals", []),
                "supporting_signals": representative.get("supporting_signals", []),
                "common_root_cause": representative.get("common_root_cause"),
                "affected_contract_ids": contract_ids,
                "representative_scenarios": sorted(
                    {str(r.get("representative_scenario")) for r in rows}
                ),
                "recommended_actions_v1": representative.get("recommended_actions", []),
            }
        )
    return library
