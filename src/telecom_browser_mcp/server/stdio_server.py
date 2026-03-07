from __future__ import annotations

from telecom_browser_mcp.server.app import TelecomBrowserApp

TOOL_NAMES = [
    "open_app",
    "login_agent",
    "wait_for_ready",
    "list_sessions",
    "close_session",
    "reset_session",
    "get_registration_status",
    "wait_for_registration",
    "assert_registered",
    "wait_for_incoming_call",
    "answer_call",
    "hangup_call",
    "get_ui_call_state",
    "get_active_session_snapshot",
    "get_store_snapshot",
    "get_peer_connection_summary",
    "get_webrtc_stats",
    "get_environment_snapshot",
    "screenshot",
    "collect_browser_logs",
    "collect_debug_bundle",
    "diagnose_registration_failure",
    "diagnose_incoming_call_failure",
    "diagnose_answer_failure",
    "diagnose_one_way_audio",
]


def _register_tools_with_fastmcp(server, app: TelecomBrowserApp) -> None:
    def _make_tool(name: str):
        async def _tool(**kwargs):
            return await app.dispatch(name, **kwargs)

        _tool.__name__ = name
        return _tool

    for tool_name in TOOL_NAMES:
        server.tool()(_make_tool(tool_name))


def main() -> None:
    app = TelecomBrowserApp()
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        raise SystemExit(
            "mcp SDK is unavailable; install dependencies with `pip install -e .[dev]` "
            f"(import error: {exc})"
        )

    server = FastMCP("telecom-browser-mcp")
    _register_tools_with_fastmcp(server, app)
    server.run(transport="stdio")


async def quickstart_smoke() -> dict:
    app = TelecomBrowserApp()
    opened = await app.dispatch("open_app", url="http://localhost:3000", adapter_name="harness")
    session_id = opened["data"].get("session_id") if opened.get("ok") else None
    sessions = await app.dispatch("list_sessions")
    if session_id:
        await app.dispatch("close_session", session_id=session_id)
    return {"open_app": opened, "list_sessions": sessions}


if __name__ == "__main__":
    main()
