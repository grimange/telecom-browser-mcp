from __future__ import annotations

import socket

import pytest

from telecom_browser_mcp.browser.manager import BrowserRequestGuard
from telecom_browser_mcp.browser.url_policy import URLPolicy


class _FakeRoute:
    def __init__(self) -> None:
        self.action: str | None = None
        self.error_code: str | None = None

    async def abort(self, error_code: str = "failed") -> None:
        self.action = "abort"
        self.error_code = error_code

    async def continue_(self) -> None:
        self.action = "continue"


class _FakeRequest:
    def __init__(self, url: str, resource_type: str = "document", navigation: bool = True) -> None:
        self.url = url
        self.resource_type = resource_type
        self._navigation = navigation

    def is_navigation_request(self) -> bool:
        return self._navigation


def _dns(*addresses: str):
    def fake_getaddrinfo(host: str, port: int | None, type: int = 0):  # noqa: A002
        return [
            (socket.AF_INET6 if ":" in address else socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port or 0))
            for address in addresses
        ]

    return fake_getaddrinfo


@pytest.mark.asyncio
async def test_secondary_request_to_localhost_is_blocked_by_default() -> None:
    route = _FakeRoute()
    guard = BrowserRequestGuard()

    await guard.handle_route(route, _FakeRequest("http://127.0.0.1:8080/api", "fetch", False))

    assert route.action == "abort"
    assert route.error_code == "blockedbyclient"
    assert guard.blocked_requests[0].reason_code == "unsafe_resolved_address"
    assert guard.blocked_requests[0].resource_type == "fetch"


@pytest.mark.asyncio
async def test_harness_local_request_is_allowed_when_explicitly_configured() -> None:
    route = _FakeRoute()
    guard = BrowserRequestGuard(URLPolicy(allowed_hosts=("127.0.0.1",), allow_local_targets=True))

    await guard.handle_route(route, _FakeRequest("http://127.0.0.1:8080/fake", "document", True))

    assert route.action == "continue"
    assert guard.blocked_requests == []


@pytest.mark.asyncio
async def test_redirect_to_blocked_target_is_blocked() -> None:
    route = _FakeRoute()
    guard = BrowserRequestGuard(URLPolicy(allowed_hosts=("example.com",)))

    await guard.handle_route(route, _FakeRequest("http://127.0.0.1:8080/redirected", "document", True))

    assert route.action == "abort"
    assert guard.blocked_requests[0].is_navigation_request is True
    assert guard.blocked_requests[0].reason_code in {"host_not_allowed", "unsafe_resolved_address"}


@pytest.mark.asyncio
async def test_iframe_document_navigation_to_blocked_target_is_blocked() -> None:
    route = _FakeRoute()
    guard = BrowserRequestGuard()

    await guard.handle_route(route, _FakeRequest("http://169.254.169.254/latest", "document", True))

    assert route.action == "abort"
    assert guard.blocked_requests[0].url == "http://169.254.169.254/latest"
    assert guard.blocked_requests[0].reason_code == "unsafe_resolved_address"


@pytest.mark.asyncio
async def test_allowed_public_subresource_continues(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", _dns("93.184.216.34"))
    route = _FakeRoute()
    guard = BrowserRequestGuard(URLPolicy(allowed_hosts=("example.com",)))

    await guard.handle_route(route, _FakeRequest("https://example.com/app.js", "script", False))

    assert route.action == "continue"
    assert guard.blocked_requests == []
