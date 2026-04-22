from __future__ import annotations

import pytest

from telecom_browser_mcp.server.transport_security import (
    StaticBearerTokenVerifier,
    TransportSecurityConfig,
    TransportSecurityError,
    auth_components,
    validate_transport_security,
)


def test_local_http_transport_can_run_without_token() -> None:
    config = TransportSecurityConfig(host="127.0.0.1", token=None, unsafe_bind_opt_in=False)

    validate_transport_security("streamable-http", config)


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.0.2.10"])
def test_non_local_bind_without_opt_in_fails_closed(host: str) -> None:
    config = TransportSecurityConfig(host=host, token=None, unsafe_bind_opt_in=False)

    with pytest.raises(TransportSecurityError):
        validate_transport_security("sse", config)


def test_non_local_bind_with_opt_in_without_token_fails_closed() -> None:
    config = TransportSecurityConfig(host="0.0.0.0", token=None, unsafe_bind_opt_in=True)

    with pytest.raises(TransportSecurityError):
        validate_transport_security("streamable-http", config)


@pytest.mark.asyncio
async def test_token_protected_transport_config_is_accepted() -> None:
    config = TransportSecurityConfig(host="0.0.0.0", token="synthetic-token", unsafe_bind_opt_in=True)

    validate_transport_security("sse", config)
    auth, verifier = auth_components(config)

    assert auth is not None
    assert isinstance(verifier, StaticBearerTokenVerifier)
    assert await verifier.verify_token("synthetic-token") is not None
    assert await verifier.verify_token("wrong-token") is None
