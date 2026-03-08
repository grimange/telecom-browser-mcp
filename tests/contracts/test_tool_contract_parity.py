from __future__ import annotations

import inspect
import json

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from telecom_browser_mcp.server.app import TelecomBrowserApp
from telecom_browser_mcp.server.stdio_server import TOOL_NAMES, _register_tools_with_fastmcp


def _build_server() -> tuple[TelecomBrowserApp, FastMCP]:
    app = TelecomBrowserApp()
    server = FastMCP("telecom-browser-mcp-contract-tests")
    _register_tools_with_fastmcp(server, app)
    return app, server


def _tool_map(tools) -> dict[str, object]:
    return {tool.name: tool for tool in tools}


@pytest.mark.asyncio
async def test_tool_listing_matches_catalog() -> None:
    _, server = _build_server()
    tools = await server.list_tools()
    assert {tool.name for tool in tools} == set(TOOL_NAMES)


@pytest.mark.asyncio
async def test_valid_invocation_noarg_tool() -> None:
    _, server = _build_server()
    call_result = await server.call_tool("list_sessions", {})
    if isinstance(call_result, tuple):
        _content, meta = call_result
        result = meta["result"]
    else:
        result = call_result[0].model_dump()["text"]
        result = json.loads(result)
    assert result["ok"] is True
    assert result["message"] == "sessions listed"
    assert result["data"]["count"] == 0
    assert result["data"]["sessions"] == []


@pytest.mark.asyncio
async def test_invalid_envelope_rejected_for_noarg_tool() -> None:
    _, server = _build_server()
    with pytest.raises(ToolError, match="Extra inputs are not permitted"):
        await server.call_tool("list_sessions", {"kwargs": {}})


@pytest.mark.asyncio
async def test_noarg_tools_publish_empty_object_schema() -> None:
    _, server = _build_server()
    by_name = _tool_map(await server.list_tools())
    for tool_name in ("health", "list_sessions"):
        schema = by_name[tool_name].inputSchema
        assert schema.get("type") == "object"
        assert schema.get("properties") == {}
        assert schema.get("required", []) == []


@pytest.mark.asyncio
async def test_all_tools_publish_strict_input_schema() -> None:
    _, server = _build_server()
    tools = await server.list_tools()
    for tool in tools:
        assert tool.inputSchema.get("additionalProperties") is False


@pytest.mark.asyncio
async def test_signature_schema_parity_for_registered_tools() -> None:
    app, server = _build_server()
    by_name = _tool_map(await server.list_tools())

    for tool_name in TOOL_NAMES:
        handler = getattr(app.orchestrator, tool_name)
        signature = inspect.signature(handler)
        params = [p for p in signature.parameters.values() if p.name != "self"]

        expected_properties = sorted(p.name for p in params)
        expected_required = sorted(p.name for p in params if p.default is inspect.Parameter.empty)

        schema = by_name[tool_name].inputSchema
        actual_properties = sorted(schema.get("properties", {}).keys())
        actual_required = sorted(schema.get("required", []))

        assert actual_properties == expected_properties
        assert actual_required == expected_required
