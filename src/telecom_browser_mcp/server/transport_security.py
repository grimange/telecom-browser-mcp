from __future__ import annotations

import hmac
import ipaddress
import os
from dataclasses import dataclass

from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
AUTH_TOKEN_ENV = "TELECOM_BROWSER_MCP_AUTH_TOKEN"  # nosec B105
UNSAFE_BIND_ENV = "TELECOM_BROWSER_MCP_UNSAFE_BIND"


class TransportSecurityError(RuntimeError):
    pass


@dataclass(frozen=True)
class TransportSecurityConfig:
    host: str
    token: str | None
    unsafe_bind_opt_in: bool

    @property
    def is_local_bind(self) -> bool:
        return _is_local_host(self.host)


class StaticBearerTokenVerifier:
    def __init__(self, expected_token: str) -> None:
        self._expected_token = expected_token

    async def verify_token(self, token: str) -> AccessToken | None:
        if not hmac.compare_digest(token, self._expected_token):
            return None
        return AccessToken(token=token, client_id="telecom-browser-mcp-static-token", scopes=[])


def _is_enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _is_local_host(host: str) -> bool:
    normalized = host.strip().strip("[]").lower()
    if normalized in LOCAL_HOSTS:
        return True
    try:
        ip = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    return ip.is_loopback


def load_transport_security_config(host: str) -> TransportSecurityConfig:
    return TransportSecurityConfig(
        host=host,
        token=os.environ.get(AUTH_TOKEN_ENV),
        unsafe_bind_opt_in=_is_enabled(os.environ.get(UNSAFE_BIND_ENV)),
    )


def validate_transport_security(transport: str, config: TransportSecurityConfig) -> None:
    if transport not in {"sse", "streamable-http"}:
        return
    if config.is_local_bind:
        return
    if not config.unsafe_bind_opt_in:
        raise TransportSecurityError(
            f"{transport} transport refuses non-local FASTMCP_HOST={config.host!r}; "
            f"set {UNSAFE_BIND_ENV}=1 and {AUTH_TOKEN_ENV} to a strong token only for a protected deployment"
        )
    if not config.token:
        raise TransportSecurityError(
            f"{transport} transport on non-local FASTMCP_HOST={config.host!r} requires "
            f"{AUTH_TOKEN_ENV}; unauthenticated network HTTP/SSE is not allowed"
        )


def auth_components(config: TransportSecurityConfig) -> tuple[AuthSettings | None, StaticBearerTokenVerifier | None]:
    if not config.token:
        return None, None
    issuer = "http://127.0.0.1"
    return (
        AuthSettings(issuer_url=issuer, resource_server_url=issuer),
        StaticBearerTokenVerifier(config.token),
    )
