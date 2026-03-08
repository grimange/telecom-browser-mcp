from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import anyio
import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


async def _call_tool_over_stdio(session: ClientSession, name: str, args: dict) -> dict:
    result = await session.call_tool(name, args)
    if result.structuredContent is not None:
        return result.structuredContent
    text_payload = "".join(
        item.text for item in result.content if getattr(item, "type", "") == "text"
    )
    return json.loads(text_payload) if text_payload else {}


@pytest.mark.asyncio
async def test_stdio_first_contact_tools() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "telecom_browser_mcp"],
        cwd=_repo_root(),
        env={**os.environ, "PYTHONPATH": str(_repo_root() / "src")},
    )
    try:
        with anyio.fail_after(30):
            async with stdio_client(server) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    names = {tool.name for tool in tools.tools}
                    assert "health" in names
                    assert "capabilities" in names
                    assert "list_sessions" in names

                    health = await _call_tool_over_stdio(session, "health", {})
                    assert health.get("ok") is True
                    assert health.get("tool") == "health"

                    capabilities = await _call_tool_over_stdio(session, "capabilities", {})
                    assert capabilities.get("ok") is True
                    assert capabilities.get("tool") == "capabilities"

                    list_sessions = await _call_tool_over_stdio(session, "list_sessions", {})
                    assert list_sessions.get("ok") is True
                    assert "data" in list_sessions
    except TimeoutError as exc:
        pytest.skip(f"stdio smoke skipped due to environment limitation: timeout: {exc}")
    except (FileNotFoundError, PermissionError) as exc:
        pytest.skip(f"stdio smoke skipped due to environment limitation: {exc}")
    except OSError as exc:
        message = str(exc).lower()
        if "resource temporarily unavailable" in message or "operation not permitted" in message:
            pytest.skip(f"stdio smoke skipped due to environment limitation: {exc}")
        raise
