from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from telecom_browser_mcp.sessions.manager import SessionRuntime

ENVIRONMENT_LIMITATION = "environment_limitation"
ADAPTER_CONTRACT_FAILURE = "adapter_contract_failure"
UI_DRIFT = "ui_drift"
REGISTRATION_RUNTIME_FAILURE = "registration_runtime_failure"
CALL_DELIVERY_FAILURE = "call_delivery_failure"
MEDIA_PATH_FAILURE = "media_path_failure"
STATE_DIVERGENCE = "state_divergence"

CANONICAL_FAILURE_CLASSES = {
    ENVIRONMENT_LIMITATION,
    ADAPTER_CONTRACT_FAILURE,
    UI_DRIFT,
    REGISTRATION_RUNTIME_FAILURE,
    CALL_DELIVERY_FAILURE,
    MEDIA_PATH_FAILURE,
    STATE_DIVERGENCE,
}

_CANONICAL_ALIASES = {
    "adapter_not_supported": ADAPTER_CONTRACT_FAILURE,
    "adapter_contract_failure": ADAPTER_CONTRACT_FAILURE,
    "environment_limit_missing_browser_binary": ENVIRONMENT_LIMITATION,
    "environment_limit_unreachable_target": ENVIRONMENT_LIMITATION,
    "permission_blocked": ENVIRONMENT_LIMITATION,
    "registration_missing": REGISTRATION_RUNTIME_FAILURE,
    "registration_runtime_failure": REGISTRATION_RUNTIME_FAILURE,
    "incoming_call_not_present": CALL_DELIVERY_FAILURE,
    "answer_action_failed": CALL_DELIVERY_FAILURE,
    "call_delivery_failure": CALL_DELIVERY_FAILURE,
    "selector_contract_missing": UI_DRIFT,
    "ui_drift": UI_DRIFT,
    "state_divergence": STATE_DIVERGENCE,
    "media_path_failure": MEDIA_PATH_FAILURE,
}


@dataclass(frozen=True)
class VerdictSummary:
    verdict: str
    canonical_classification: str
    environment_vs_product: str


def canonicalize_classification(classification: str | None) -> str:
    if not classification:
        return "unknown"
    return _CANONICAL_ALIASES.get(classification, classification)


def classify_target(runtime: SessionRuntime) -> str:
    host = (urlparse(runtime.model.target_url).hostname or "").lower()
    if runtime.model.adapter_id == "apntalk" or host.endswith("apntalk.com"):
        return "apntalk"
    if runtime.model.adapter_id == "fake_dialer":
        return "fake_dialer"
    return "generic_web"


def summarize_verdict(
    runtime: SessionRuntime,
    diagnostics: list[dict[str, Any]],
) -> VerdictSummary:
    classifications = [
        canonicalize_classification(item.get("classification"))
        for item in diagnostics
        if item.get("classification")
    ]
    if runtime.model.browser_launch_error_classification:
        classifications.insert(
            0, canonicalize_classification(runtime.model.browser_launch_error_classification)
        )

    canonical_classification = classifications[0] if classifications else "unknown"
    if canonical_classification == "unknown" and runtime.model.lifecycle_state == "ready":
        verdict = "ok"
    else:
        verdict = "failed"

    if canonical_classification == ENVIRONMENT_LIMITATION:
        environment_vs_product = "environment"
    elif canonical_classification in {ADAPTER_CONTRACT_FAILURE, UI_DRIFT, STATE_DIVERGENCE}:
        environment_vs_product = "adapter_or_ui"
    else:
        environment_vs_product = "product_or_runtime"

    return VerdictSummary(
        verdict=verdict,
        canonical_classification=canonical_classification,
        environment_vs_product=environment_vs_product,
    )
