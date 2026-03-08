from __future__ import annotations

import os
import sys

import anyio
import mcp.types as mcp_types
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase
from mcp.shared.message import SessionMessage
from pydantic import ConfigDict

from telecom_browser_mcp.server.app import TelecomBrowserApp

TOOL_NAMES = [
    "health",
    "capabilities",
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
    # Force strict tool arguments so tools/list schema and runtime both reject unknown fields.
    if ArgModelBase.model_config.get("extra") != "forbid":
        ArgModelBase.model_config = ConfigDict(**ArgModelBase.model_config, extra="forbid")
        ArgModelBase.model_rebuild(force=True)

    for tool_name in TOOL_NAMES:
        handler = getattr(app.orchestrator, tool_name, None)
        if handler is None:
            raise ValueError(f"missing orchestrator handler for tool: {tool_name}")
        # Contract invariant: register bound orchestrator handlers directly.
        # Do not reintroduce synthetic wrapper callables (for example `**kwargs`) because
        # they can drift public schemas away from runtime signatures.
        server.tool(name=tool_name)(handler)


async def _run_stdio_server_safe(server) -> None:
    read_stream: MemoryObjectReceiveStream[SessionMessage | Exception]
    read_writer: MemoryObjectSendStream[SessionMessage | Exception]
    write_stream: MemoryObjectSendStream[SessionMessage]
    write_reader: MemoryObjectReceiveStream[SessionMessage]
    read_writer, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_reader = anyio.create_memory_object_stream(0)

    def _read_line() -> str:
        return sys.stdin.readline()

    def _write_line(payload: str) -> None:
        sys.stdout.write(payload + "\n")
        sys.stdout.flush()

    async def _stdin_reader() -> None:
        async with read_writer:
            while True:
                line = await anyio.to_thread.run_sync(_read_line)
                if line == "":
                    break
                try:
                    message = mcp_types.JSONRPCMessage.model_validate_json(line)
                except Exception as exc:
                    await read_writer.send(exc)
                    continue
                await read_writer.send(SessionMessage(message))

    async def _stdout_writer() -> None:
        async with write_reader:
            async for session_message in write_reader:
                payload = session_message.message.model_dump_json(by_alias=True, exclude_none=True)
                await anyio.to_thread.run_sync(_write_line, payload)

    async with anyio.create_task_group() as tg:
        tg.start_soon(_stdin_reader)
        tg.start_soon(_stdout_writer)
        await server._mcp_server.run(
            read_stream,
            write_stream,
            server._mcp_server.create_initialization_options(),
        )


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
    use_sdk_stdio = os.getenv("TELECOM_BROWSER_MCP_USE_SDK_STDIO", "false").lower() == "true"
    if use_sdk_stdio:
        server.run(transport="stdio")
        return
    anyio.run(_run_stdio_server_safe, server)


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
