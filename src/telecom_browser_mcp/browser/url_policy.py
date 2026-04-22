from __future__ import annotations

import fnmatch
import ipaddress
import os
import socket
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ALLOWED_HOSTS_ENV = "TELECOM_BROWSER_MCP_ALLOWED_HOSTS"
ALLOW_LOCAL_ENV = "TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS"

_SAFE_SCHEMES = {"http", "https"}
_SENSITIVE_QUERY_KEYS = {"token", "key", "secret", "password", "session", "auth", "api_key"}
_METADATA_IPS = {ipaddress.ip_address("169.254.169.254")}


class URLPolicyError(ValueError):
    def __init__(self, reason_code: str, message: str, safe_target: str) -> None:
        self.reason_code = reason_code
        self.safe_target = safe_target
        super().__init__(message)


@dataclass(frozen=True)
class URLPolicy:
    allowed_hosts: tuple[str, ...] = field(default_factory=tuple)
    allow_local_targets: bool = False


def _enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def load_url_policy() -> URLPolicy:
    allowed = tuple(
        item.strip().lower()
        for item in os.environ.get(ALLOWED_HOSTS_ENV, "").split(",")
        if item.strip()
    )
    return URLPolicy(allowed_hosts=allowed, allow_local_targets=_enabled(os.environ.get(ALLOW_LOCAL_ENV)))


def sanitize_url_for_metadata(raw_url: str) -> str:
    try:
        parsed = urlsplit(raw_url)
    except ValueError:
        return "[invalid-url]"
    query = urlencode(
        [
            (key, "[REDACTED]" if key.lower() in _SENSITIVE_QUERY_KEYS else value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        ],
        doseq=True,
    )
    netloc = parsed.hostname or "[missing-host]"
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, query, ""))


def validate_target_url(raw_url: str, policy: URLPolicy | None = None) -> str:
    policy = policy or load_url_policy()
    safe_target = sanitize_url_for_metadata(raw_url)
    try:
        parsed = urlsplit(raw_url)
    except ValueError as exc:
        raise URLPolicyError("invalid_url", "target_url is not a valid URL", safe_target) from exc

    scheme = parsed.scheme.lower()
    if scheme not in _SAFE_SCHEMES:
        raise URLPolicyError("blocked_scheme", "target_url scheme is not allowed", safe_target)
    if not parsed.hostname:
        raise URLPolicyError("missing_host", "target_url must include a hostname", safe_target)

    host = parsed.hostname.lower()
    if policy.allowed_hosts and not any(fnmatch.fnmatch(host, pattern) for pattern in policy.allowed_hosts):
        raise URLPolicyError("host_not_allowed", "target_url host is not in the allowlist", safe_target)

    resolved = _resolve_host(host)
    if not resolved:
        raise URLPolicyError("dns_resolution_failed", "target_url host could not be resolved", safe_target)

    unsafe_ips = [ip for ip in resolved if _is_unsafe_ip(ip)]
    if unsafe_ips and not _host_explicitly_allowed_for_local(host, policy):
        raise URLPolicyError("unsafe_resolved_address", "target_url resolves to a local or private address", safe_target)

    return raw_url


def _host_explicitly_allowed_for_local(host: str, policy: URLPolicy) -> bool:
    if not policy.allow_local_targets:
        return False
    return bool(policy.allowed_hosts) and any(fnmatch.fnmatch(host, pattern) for pattern in policy.allowed_hosts)


def _resolve_host(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    try:
        return [ipaddress.ip_address(host)]
    except ValueError:
        pass

    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return []
    resolved: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    for info in infos:
        address = info[4][0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue
        if ip not in resolved:
            resolved.append(ip)
    return resolved


def _is_unsafe_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip in _METADATA_IPS
        or ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )
