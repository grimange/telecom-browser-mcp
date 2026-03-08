from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from telecom_browser_mcp.contracts import CANONICAL_TOOL_INPUT_MODELS
from telecom_browser_mcp.tools.service import ToolService


def create_mcp_server() -> FastMCP:
    mcp = FastMCP("telecom-browser-mcp")
    service = ToolService()

    async def dispatch(tool_name: str, payload: dict[str, Any]) -> dict:
        handler = getattr(service, tool_name)
        return await handler(payload)

    @mcp.tool()
    async def health() -> dict:
        return await dispatch("health", {})

    @mcp.tool()
    async def capabilities() -> dict:
        return await dispatch("capabilities", {})

    @mcp.tool()
    async def open_app(target_url: str, adapter_id: str | None = None, headless: bool = True, session_label: str | None = None) -> dict:
        return await dispatch("open_app", {"target_url": target_url, "adapter_id": adapter_id, "headless": headless, "session_label": session_label})

    @mcp.tool()
    async def list_sessions() -> dict:
        return await dispatch("list_sessions", {})

    @mcp.tool()
    async def close_session(session_id: str) -> dict:
        return await dispatch("close_session", {"session_id": session_id})

    @mcp.tool()
    async def login_agent(session_id: str, credentials: dict[str, Any] | None = None, timeout_ms: int = 15000) -> dict:
        return await dispatch("login_agent", {"session_id": session_id, "credentials": credentials or {}, "timeout_ms": timeout_ms})

    @mcp.tool()
    async def wait_for_ready(session_id: str, timeout_ms: int = 15000) -> dict:
        return await dispatch("wait_for_ready", {"session_id": session_id, "timeout_ms": timeout_ms})

    @mcp.tool()
    async def wait_for_registration(session_id: str, timeout_ms: int = 15000) -> dict:
        return await dispatch("wait_for_registration", {"session_id": session_id, "timeout_ms": timeout_ms})

    @mcp.tool()
    async def wait_for_incoming_call(session_id: str, timeout_ms: int = 15000) -> dict:
        return await dispatch("wait_for_incoming_call", {"session_id": session_id, "timeout_ms": timeout_ms})

    @mcp.tool()
    async def answer_call(session_id: str, timeout_ms: int = 15000) -> dict:
        return await dispatch("answer_call", {"session_id": session_id, "timeout_ms": timeout_ms})

    @mcp.tool()
    async def get_active_session_snapshot(session_id: str) -> dict:
        return await dispatch("get_active_session_snapshot", {"session_id": session_id})

    @mcp.tool()
    async def get_peer_connection_summary(session_id: str) -> dict:
        return await dispatch("get_peer_connection_summary", {"session_id": session_id})

    @mcp.tool()
    async def collect_debug_bundle(session_id: str, reason: str | None = None) -> dict:
        return await dispatch("collect_debug_bundle", {"session_id": session_id, "reason": reason})

    @mcp.tool()
    async def diagnose_answer_failure(session_id: str) -> dict:
        return await dispatch("diagnose_answer_failure", {"session_id": session_id})

    assert set(CANONICAL_TOOL_INPUT_MODELS.keys()) == {
        "health",
        "capabilities",
        "open_app",
        "list_sessions",
        "close_session",
        "login_agent",
        "wait_for_ready",
        "wait_for_registration",
        "wait_for_incoming_call",
        "answer_call",
        "get_active_session_snapshot",
        "get_peer_connection_summary",
        "collect_debug_bundle",
        "diagnose_answer_failure",
    }

    return mcp
