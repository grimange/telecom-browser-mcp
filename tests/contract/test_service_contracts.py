import pytest

from telecom_browser_mcp.tools.service import ToolService


@pytest.mark.asyncio
async def test_open_app_contract_shape() -> None:
    service = ToolService()
    result = await service.open_app({"target_url": "https://example.com"})

    assert result["ok"] is True
    assert result["tool"] == "open_app"
    assert "session_id" in result["data"]
    assert result["meta"]["contract_version"] == "v1"


@pytest.mark.asyncio
async def test_rejects_undeclared_field() -> None:
    service = ToolService()
    result = await service.open_app({"target_url": "https://example.com", "unexpected": 1})
    assert result["ok"] is False
    assert result["error"]["code"] == "invalid_input"
