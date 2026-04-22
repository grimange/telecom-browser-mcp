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
            "target_url": "https://app.apntalk.com/agent",
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
