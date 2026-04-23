import pytest

from telecom_browser_mcp.browser.url_policy import URLPolicy
from telecom_browser_mcp.tools.service import ToolService


@pytest.mark.asyncio
async def test_open_app_contract_shape() -> None:
    service = ToolService()
    result = await service.open_app({"target_url": "https://example.com"})

    assert result["ok"] is True
    assert result["tool"] == "open_app"
    assert "session_id" in result["data"]
    assert "ready_for_actions" in result["data"]
    assert isinstance(result["data"]["ready_for_actions"], bool)
    assert result["meta"]["contract_version"] == result["data"]["contract_version"]
    assert result["meta"]["adapter_name"] == result["data"]["resolved_adapter_name"]
    assert result["meta"]["adapter_version"] == result["data"]["adapter_version"]
    assert result["meta"]["scenario_id"] == result["data"]["scenario_id"]


@pytest.mark.asyncio
async def test_rejects_undeclared_field() -> None:
    service = ToolService()
    result = await service.open_app({"target_url": "https://example.com", "unexpected": 1})
    assert result["ok"] is False
    assert result["error"]["code"] == "invalid_input"


@pytest.mark.asyncio
async def test_apntalk_host_rejects_explicit_generic_adapter() -> None:
    service = ToolService()

    result = await service.open_app(
        {
            "target_url": "https://s022-067.apntelecom.com/agent",
            "adapter_id": "generic",
        }
    )

    assert result["ok"] is False
    assert result["error"]["code"] == "adapter_target_mismatch"
    assert result["error"]["classification"] == "adapter_contract_failure"


@pytest.mark.asyncio
async def test_capabilities_exposes_adapter_descriptors() -> None:
    service = ToolService()

    result = await service.capabilities({})

    assert result["ok"] is True
    adapter_ids = {adapter["adapter_id"] for adapter in result["data"]["adapters"]}
    assert {"generic", "apntalk", "fake_dialer"}.issubset(adapter_ids)
    apntalk = next(adapter for adapter in result["data"]["adapters"] if adapter["adapter_id"] == "apntalk")
    bridge_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "apntalk_runtime_bridge_contract"
    )
    ready_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "wait_for_ready")
    registration_wait_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "wait_for_registration"
    )
    incoming_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "wait_for_incoming_call"
    )
    registration_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "get_registration_status"
    )
    peer_connection_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "get_peer_connection_summary"
    )
    answer_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "answer_call")
    hangup_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "hangup_call")
    store_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "get_store_snapshot")
    assert bridge_truth["declared_support"] == "supported_with_runtime_probe"
    assert ready_truth["declared_support"] == "supported_with_runtime_probe"
    assert registration_wait_truth["declared_support"] == "supported_with_runtime_probe"
    assert incoming_truth["declared_support"] == "supported_with_runtime_probe"
    assert registration_truth["declared_support"] == "supported_with_runtime_probe"
    assert peer_connection_truth["declared_support"] == "supported_with_runtime_probe"
    assert answer_truth["declared_support"] == "supported_with_selector_binding"
    assert hangup_truth["declared_support"] == "supported_with_selector_binding"
    assert store_truth["declared_support"] == "scaffold_only"
    assert store_truth["binding_status"] == "unbound"


@pytest.mark.asyncio
async def test_open_app_rejects_unsafe_local_target_by_default() -> None:
    service = ToolService()

    result = await service.open_app({"target_url": "http://127.0.0.1:8000"})

    assert result["ok"] is False
    assert result["error"]["code"] == "target_url_blocked"
    assert result["error"]["classification"] == "security_policy"
    assert result["diagnostics"][0]["code"] == "unsafe_resolved_address"


@pytest.mark.asyncio
async def test_open_app_harness_allow_mode_permits_explicit_local_host() -> None:
    service = ToolService(url_policy=URLPolicy(allowed_hosts=("127.0.0.1",), allow_local_targets=True))

    result = await service.open_app({"target_url": "http://127.0.0.1:9", "adapter_id": "fake_dialer"})

    assert result["ok"] is True
    assert result["data"]["resolved_adapter_id"] == "fake_dialer"
