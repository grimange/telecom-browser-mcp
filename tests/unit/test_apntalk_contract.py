from __future__ import annotations

import pytest

from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.apntalk_contract import (
    APNTALK_SURFACE_CONTRACTS,
    apntalk_contract_drift_report,
)
from telecom_browser_mcp.models.session import TelecomStatus


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "expected_code", "expected_classification"),
    [
        ("login", "adapter_contract_unimplemented", "adapter_contract_failure"),
        ("wait_for_ready", "selector_contract_missing", "ui_drift"),
        ("wait_for_registration", "runtime_probe_unavailable", "adapter_contract_failure"),
        ("wait_for_incoming_call", "runtime_probe_unavailable", "adapter_contract_failure"),
        ("answer_call", "adapter_contract_unimplemented", "adapter_contract_failure"),
        ("hangup_call", "adapter_contract_unimplemented", "adapter_contract_failure"),
    ],
)
async def test_apntalk_operations_fail_closed(
    method_name: str,
    expected_code: str,
    expected_classification: str,
) -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    if method_name == "login":
        result = await adapter.login(status, page=object(), credentials={}, timeout_ms=100)
    else:
        result = await getattr(adapter, method_name)(status, page=object(), timeout_ms=100)

    assert result.ok is False
    assert result.error_code == expected_code
    assert result.classification == expected_classification
    assert result.details["missing_requirements"]


@pytest.mark.asyncio
async def test_apntalk_wait_for_ready_does_not_inherit_scaffold_success() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    result = await adapter.wait_for_ready(status, page=object(), timeout_ms=100)

    assert result.ok is False
    assert result.error_code == "selector_contract_missing"
    assert status.ui_ready is False
    assert result.details["missing_requirements"] == ["selector:agent_ready_indicator"]


def test_apntalk_contract_drift_report_tracks_unimplemented_surfaces() -> None:
    report = apntalk_contract_drift_report()

    assert set(report) == set(APNTALK_SURFACE_CONTRACTS)
    assert report["wait_for_registration"] == [
        "selector:registration_badge",
        "runtime_probe:registration_snapshot",
    ]


@pytest.mark.asyncio
async def test_apntalk_snapshot_surfaces_fail_closed() -> None:
    adapter = APNTalkAdapter()
    status = TelecomStatus()

    registration = await adapter.registration_snapshot(status, page=object())
    store = await adapter.store_snapshot(status, page=object())

    assert registration["available"] is False
    assert registration["reason_code"] == "runtime_probe_unavailable"
    assert store["available"] is False
    assert store["reason_code"] == "runtime_probe_unavailable"
