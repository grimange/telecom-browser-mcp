from __future__ import annotations

import socket

import pytest

from telecom_browser_mcp.browser.url_policy import URLPolicy, URLPolicyError, validate_target_url


def _dns(*addresses: str):
    def fake_getaddrinfo(host: str, port: int | None, type: int = 0):  # noqa: A002
        return [
            (socket.AF_INET6 if ":" in address else socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port or 0))
            for address in addresses
        ]

    return fake_getaddrinfo


def test_valid_allowed_https_host_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", _dns("93.184.216.34"))

    assert (
        validate_target_url("https://example.com/app", URLPolicy(allowed_hosts=("example.com",)))
        == "https://example.com/app"
    )


def test_disallowed_host_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", _dns("93.184.216.34"))

    with pytest.raises(URLPolicyError) as exc:
        validate_target_url("https://evil.example/app", URLPolicy(allowed_hosts=("example.com",)))

    assert exc.value.reason_code == "host_not_allowed"


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://10.0.0.5",
        "http://192.168.1.5",
        "http://[fd00::1]/",
        "http://169.254.169.254/latest/meta-data/",
    ],
)
def test_local_private_and_metadata_targets_fail(url: str) -> None:
    with pytest.raises(URLPolicyError) as exc:
        validate_target_url(url, URLPolicy())

    assert exc.value.reason_code == "unsafe_resolved_address"


@pytest.mark.parametrize("scheme", ["file", "data", "chrome", "about", "javascript", "ws", "wss"])
def test_unsafe_schemes_fail(scheme: str) -> None:
    suffix = "alert(1)" if scheme == "javascript" else "//example.com/app"

    with pytest.raises(URLPolicyError) as exc:
        validate_target_url(f"{scheme}:{suffix}", URLPolicy())

    assert exc.value.reason_code == "blocked_scheme"


def test_harness_local_allow_mode_requires_explicit_host_allowlist() -> None:
    policy = URLPolicy(allowed_hosts=("127.0.0.1",), allow_local_targets=True)

    assert validate_target_url("http://127.0.0.1:9000/fake", policy) == "http://127.0.0.1:9000/fake"
