from __future__ import annotations

from typing import Any

MATCH_SCALE = ["none", "weak", "moderate", "strong", "exact"]


def match_signature(
    normalized_signal: dict[str, Any],
    signatures: list[dict[str, Any]],
) -> dict[str, Any]:
    best = {
        "signature_id": None,
        "match_strength": "none",
        "matched_rules": [],
        "unmatched_signals": [],
        "recommended_actions": [],
    }
    for signature in signatures:
        trigger_signals = list(signature.get("trigger_signals", []))
        matched = [signal for signal in trigger_signals if normalized_signal.get(signal)]
        ratio = (len(matched) / len(trigger_signals)) if trigger_signals else 0.0
        strength = _ratio_to_strength(ratio)
        if MATCH_SCALE.index(strength) <= MATCH_SCALE.index(best["match_strength"]):
            continue
        unmatched = [signal for signal in trigger_signals if signal not in matched]
        best = {
            "signature_id": signature.get("signature_id"),
            "match_strength": strength,
            "matched_rules": matched,
            "unmatched_signals": unmatched,
            "recommended_actions": signature.get("recommended_actions", []),
        }
    return best


def _ratio_to_strength(ratio: float) -> str:
    if ratio == 1.0:
        return "exact"
    if ratio >= 0.75:
        return "strong"
    if ratio >= 0.5:
        return "moderate"
    if ratio > 0.0:
        return "weak"
    return "none"
