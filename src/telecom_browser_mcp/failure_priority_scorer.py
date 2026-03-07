from __future__ import annotations

from typing import Any

SEVERITY_BY_CATEGORY = {
    "selector_stale_after_dom_refresh": 30,
    "page_closed_before_action": 28,
    "javascript_runtime_error": 24,
    "network_failure_ui_timeout": 22,
    "context_invalidated_during_wait": 20,
    "diagnostics_bundle_missing_on_failure": 12,
    "environment_blocked_execution": 6,
}

NOVELTY_SCORE = {
    "new_signature": 30,
    "known_but_regressing": 20,
    "known_signature": 5,
    "unknown_unmatched": 35,
}

CONFIDENCE_SCORE = {
    "exact": 10,
    "strong": 8,
    "moderate": 5,
    "weak": 2,
    "none": 0,
}

DOMAIN_BONUS = {
    "product_logic": 10,
    "browser_lifecycle_or_harness": 6,
    "diagnostics_pipeline": 3,
    "environment_or_ci": -5,
    "contract_definition": 1,
}


def classify_domain(signature: dict[str, Any]) -> str:
    category = str(signature.get("category", ""))
    if category in {
        "selector_stale_after_dom_refresh",
        "page_closed_before_action",
        "javascript_runtime_error",
        "network_failure_ui_timeout",
    }:
        return "product_logic"
    if category in {"context_invalidated_during_wait"}:
        return "browser_lifecycle_or_harness"
    if category in {"diagnostics_bundle_missing_on_failure"}:
        return "diagnostics_pipeline"
    if category in {"environment_blocked_execution"}:
        return "environment_or_ci"
    return "contract_definition"


def score_signature(
    signature: dict[str, Any],
    *,
    novelty_classification: str,
) -> dict[str, Any]:
    category = str(signature.get("category", ""))
    domain = classify_domain(signature)
    occurrence_count = int(signature.get("occurrence_count", 0))
    contract_count = len(signature.get("contract_ids", []))
    confidence = str(signature.get("confidence_notes", "weak"))

    severity = SEVERITY_BY_CATEGORY.get(category, 10)
    novelty = NOVELTY_SCORE.get(novelty_classification, 0)
    frequency = min(20, occurrence_count * 2)
    contract_impact = min(20, contract_count * 2)
    trend = 10 if novelty_classification == "known_but_regressing" else 0
    confidence_weight = CONFIDENCE_SCORE.get(confidence, 0)
    diagnostics_quality = -5 if category == "diagnostics_bundle_missing_on_failure" else 5
    domain_weight = DOMAIN_BONUS.get(domain, 0)

    score = (
        severity
        + novelty
        + frequency
        + contract_impact
        + trend
        + confidence_weight
        + diagnostics_quality
        + domain_weight
    )
    bucket = _bucket(score, domain)
    return {
        "signature_id": signature.get("signature_id"),
        "signature_name": signature.get("name"),
        "category": category,
        "domain": domain,
        "novelty_classification": novelty_classification,
        "score": score,
        "priority_bucket": bucket,
        "components": {
            "severity": severity,
            "novelty": novelty,
            "frequency": frequency,
            "contract_impact": contract_impact,
            "trend": trend,
            "confidence": confidence_weight,
            "diagnostics_quality": diagnostics_quality,
            "domain": domain_weight,
        },
        "occurrence_count": occurrence_count,
        "contract_count": contract_count,
        "contract_ids": list(signature.get("contract_ids", [])),
    }


def score_signatures(
    signatures: list[dict[str, Any]],
    novelty_by_signature_id: dict[str, str],
) -> list[dict[str, Any]]:
    ranked = [
        score_signature(
            signature,
            novelty_classification=novelty_by_signature_id.get(
                str(signature.get("signature_id", "")),
                "unknown_unmatched",
            ),
        )
        for signature in signatures
    ]
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def _bucket(score: int, domain: str) -> str:
    if domain == "environment_or_ci":
        return "P4"
    if score >= 75:
        return "P0"
    if score >= 55:
        return "P1"
    if score >= 35:
        return "P2"
    if score >= 20:
        return "P3"
    return "P4"
