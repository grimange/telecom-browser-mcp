from __future__ import annotations

from telecom_browser_mcp.server import sse_server, streamable_http_server


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
