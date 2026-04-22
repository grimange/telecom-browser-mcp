from __future__ import annotations

from telecom_browser_mcp.server import sse_server, streamable_http_server
from telecom_browser_mcp.server.transport_security import TransportSecurityError


class _FakeServer:
    def __init__(self) -> None:
        self.called_transport: str | None = None

    def run(self, transport: str | None = None) -> None:
        self.called_transport = transport


def test_sse_entrypoint_sets_sse_transport(monkeypatch) -> None:
    fake = _FakeServer()
    monkeypatch.setattr(sse_server, "create_mcp_server", lambda: fake)
    sse_server.main()
    assert fake.called_transport == "sse"


def test_streamable_http_entrypoint_sets_transport(monkeypatch) -> None:
    fake = _FakeServer()
    monkeypatch.setattr(streamable_http_server, "create_mcp_server", lambda: fake)
    streamable_http_server.main()
    assert fake.called_transport == "streamable-http"


def test_sse_entrypoint_rejects_nonlocal_bind_without_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("FASTMCP_HOST", "0.0.0.0")
    monkeypatch.delenv("TELECOM_BROWSER_MCP_UNSAFE_BIND", raising=False)
    monkeypatch.delenv("TELECOM_BROWSER_MCP_AUTH_TOKEN", raising=False)
    monkeypatch.setattr(sse_server, "create_mcp_server", lambda: _FakeServer())

    try:
        sse_server.main()
    except TransportSecurityError:
        return
    raise AssertionError("sse entrypoint accepted unsafe non-local bind")


def test_streamable_http_entrypoint_accepts_token_protected_nonlocal_bind(monkeypatch) -> None:
    fake = _FakeServer()
    monkeypatch.setenv("FASTMCP_HOST", "0.0.0.0")
    monkeypatch.setenv("TELECOM_BROWSER_MCP_UNSAFE_BIND", "1")
    monkeypatch.setenv("TELECOM_BROWSER_MCP_AUTH_TOKEN", "synthetic-token")
    monkeypatch.setattr(streamable_http_server, "create_mcp_server", lambda: fake)

    streamable_http_server.main()

    assert fake.called_transport == "streamable-http"
