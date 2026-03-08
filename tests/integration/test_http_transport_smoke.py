from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import anyio
import pytest
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client


def _require_live_transport_runtime() -> bool:
    value = os.environ.get("MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _start_server(module: str, port: int) -> subprocess.Popen:
    env = {
        **os.environ,
        "PYTHONPATH": str(_repo_root() / "src"),
        "FASTMCP_HOST": "127.0.0.1",
        "FASTMCP_PORT": str(port),
    }
    return subprocess.Popen(
        [sys.executable, "-m", module],
        cwd=_repo_root(),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def _wait_for_port(port: int, timeout_s: float = 10.0) -> None:
    deadline = anyio.current_time() + timeout_s
    while anyio.current_time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        await anyio.sleep(0.1)
    raise TimeoutError(f"server did not start on port {port}")


def _stop_server(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


async def _call_tool(session: ClientSession, name: str, args: dict) -> dict:
    result = await session.call_tool(name, args)
    if result.structuredContent is not None:
        return result.structuredContent
    text_payload = "".join(
        item.text for item in result.content if getattr(item, "type", "") == "text"
    )
    return json.loads(text_payload) if text_payload else {}


@pytest.mark.asyncio
async def test_sse_first_contact_tools_live() -> None:
    process: subprocess.Popen | None = None
    try:
        port = _pick_free_port()
        process = _start_server("telecom_browser_mcp.server.sse_server", port)
        with anyio.fail_after(30):
            await _wait_for_port(port)
            async with sse_client(f"http://127.0.0.1:{port}/sse") as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    health = await _call_tool(session, "health", {})
                    capabilities = await _call_tool(session, "capabilities", {})
                    list_sessions = await _call_tool(session, "list_sessions", {})
                    assert health.get("ok") is True
                    assert capabilities.get("ok") is True
                    assert list_sessions.get("ok") is True
    except Exception as exc:
        if _require_live_transport_runtime():
            raise
        pytest.skip(f"sse smoke skipped due to environment limitation: {exc}")
    finally:
        if process is not None:
            _stop_server(process)


@pytest.mark.asyncio
async def test_streamable_http_first_contact_tools_live() -> None:
    process: subprocess.Popen | None = None
    try:
        port = _pick_free_port()
        process = _start_server("telecom_browser_mcp.server.streamable_http_server", port)
        with anyio.fail_after(30):
            await _wait_for_port(port)
            async with streamable_http_client(f"http://127.0.0.1:{port}/mcp") as (
                read_stream,
                write_stream,
                _get_session_id,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    health = await _call_tool(session, "health", {})
                    capabilities = await _call_tool(session, "capabilities", {})
                    list_sessions = await _call_tool(session, "list_sessions", {})
                    assert health.get("ok") is True
                    assert capabilities.get("ok") is True
                    assert list_sessions.get("ok") is True
    except Exception as exc:
        if _require_live_transport_runtime():
            raise
        pytest.skip(f"streamable-http smoke skipped due to environment limitation: {exc}")
    finally:
        if process is not None:
            _stop_server(process)
