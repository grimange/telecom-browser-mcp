from __future__ import annotations

from types import SimpleNamespace

from telecom_browser_mcp.diagnostics.taxonomy import (
    ENVIRONMENT_LIMITATION,
    REGISTRATION_RUNTIME_FAILURE,
    canonicalize_classification,
    classify_target,
    summarize_verdict,
)


def _runtime(*, adapter_id: str, target_url: str, lifecycle_state: str = "degraded", browser_error: str | None = None):
    model = SimpleNamespace(
        adapter_id=adapter_id,
        target_url=target_url,
        lifecycle_state=lifecycle_state,
        browser_launch_error_classification=browser_error,
    )
    browser = SimpleNamespace(browser_open=False)
    return SimpleNamespace(model=model, browser=browser)


def test_canonicalize_classification_maps_known_aliases() -> None:
    assert canonicalize_classification("environment_limit_missing_browser_binary") == ENVIRONMENT_LIMITATION
    assert canonicalize_classification("registration_missing") == REGISTRATION_RUNTIME_FAILURE


def test_classify_target_marks_apntalk_hosts() -> None:
    runtime = _runtime(adapter_id="generic", target_url="https://app.apntalk.com/agent")
    assert classify_target(runtime) == "apntalk"


def test_summarize_verdict_distinguishes_environment_from_product() -> None:
    runtime = _runtime(
        adapter_id="generic",
        target_url="https://example.com",
        browser_error="environment_limit_missing_browser_binary",
    )
    summary = summarize_verdict(runtime, diagnostics=[])

    assert summary.verdict == "failed"
    assert summary.canonical_classification == ENVIRONMENT_LIMITATION
    assert summary.environment_vs_product == "environment"
