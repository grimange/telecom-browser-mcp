import pytest

from telecom_browser_mcp.server.stdio_server import quickstart_smoke


@pytest.mark.asyncio
async def test_quickstart_smoke() -> None:
    payload = await quickstart_smoke()
    assert payload["open_app"]["ok"] is True
    assert payload["list_sessions"]["ok"] is True
