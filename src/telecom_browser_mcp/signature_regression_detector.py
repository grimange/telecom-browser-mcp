from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RegressionRecord:
    signature_id: str
    signature_name: str
    category: str
    classification: str
    current_occurrence_count: int
    previous_occurrence_count: int
    delta: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "signature_id": self.signature_id,
            "signature_name": self.signature_name,
            "category": self.category,
            "classification": self.classification,
            "current_occurrence_count": self.current_occurrence_count,
            "previous_occurrence_count": self.previous_occurrence_count,
            "delta": self.delta,
        }


def classify_known_vs_new(
    current_signatures: list[dict[str, Any]],
    previous_signatures: list[dict[str, Any]],
) -> list[RegressionRecord]:
    previous_by_key = {
        _key(sig): sig for sig in previous_signatures if sig.get("name") and sig.get("category")
    }
    records: list[RegressionRecord] = []
    for signature in current_signatures:
        key = _key(signature)
        current_count = int(signature.get("occurrence_count", 0))
        previous = previous_by_key.get(key)
        previous_count = int(previous.get("occurrence_count", 0)) if previous else 0
        if previous is None:
            classification = "new_signature"
        elif current_count > previous_count:
            classification = "known_but_regressing"
        else:
            classification = "known_signature"
        if not signature.get("name") or not signature.get("category"):
            classification = "unknown_unmatched"

        records.append(
            RegressionRecord(
                signature_id=str(signature.get("signature_id", "")),
                signature_name=str(signature.get("name", "")),
                category=str(signature.get("category", "")),
                classification=classification,
                current_occurrence_count=current_count,
                previous_occurrence_count=previous_count,
                delta=current_count - previous_count,
            )
        )
    return records


def _key(signature: dict[str, Any]) -> tuple[str, str]:
    return (str(signature.get("name", "")), str(signature.get("category", "")))
