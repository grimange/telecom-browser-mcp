from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

REDACTION_MARKER = "[REDACTED]"
_SENSITIVE_QUERY_KEYS = {"token", "key", "secret", "password", "session", "auth", "api_key"}

_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(?i)(authorization\s*[=:]\s*bearer\s+)([^\s\"'<>;,]+)", rf"\1{REDACTION_MARKER}"),
    (r"(?i)(authorization\s*[=:]\s*)([^\s\"'<>;,]+)", rf"\1{REDACTION_MARKER}"),
    (r"(?i)(set-cookie\s*[=:]\s*)([^\"'<>;\n]+)", rf"\1{REDACTION_MARKER}"),
    (r"(?i)(cookie\s*[=:]\s*)([^\"'<>;\n]+)", rf"\1{REDACTION_MARKER}"),
    (r"(?i)((?:password|passwd|pwd)\s*[=:]\s*)([^\s\"'<>;,]+)", rf"\1{REDACTION_MARKER}"),
    (r"(?i)((?:api[_-]?key|secret|token|session[_-]?id|sid|auth)\s*[=:]\s*)([^\s\"'<>;,]+)", rf"\1{REDACTION_MARKER}"),
    (r"(?i)(sip:)[^@\s\"'<>;]+@", rf"\1{REDACTION_MARKER}@"),
    (r"\+[1-9]\d{7,14}\b", REDACTION_MARKER),
    (r"\b(?:\d[ -]?){9,15}\d\b", REDACTION_MARKER),
    (r"\b(?:10|127)\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", REDACTION_MARKER),
    (r"\b172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}\b", REDACTION_MARKER),
    (r"\b192\.168\.\d{1,3}\.\d{1,3}\b", REDACTION_MARKER),
    (r"\b169\.254\.\d{1,3}\.\d{1,3}\b", REDACTION_MARKER),
    (r"\b(?:localhost|[a-z0-9-]+\.internal|[a-z0-9-]+\.local)\b", REDACTION_MARKER),
    (r"\b(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\b", REDACTION_MARKER),
)


def redact_text(value: str) -> str:
    redacted = _redact_url_query(value)
    for pattern, replacement in _PATTERNS:
        redacted = re.sub(pattern, replacement, redacted)
    return redacted


def redact_obj(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact_obj(item) for item in value]
    if isinstance(value, dict):
        redacted: dict[Any, Any] = {}
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in _SENSITIVE_QUERY_KEYS:
                redacted[key] = REDACTION_MARKER
            else:
                redacted[key] = redact_obj(item)
        return redacted
    return value


def dumps_redacted_json(value: Any, *, indent: int = 2) -> str:
    return json.dumps(redact_obj(value), indent=indent)


def _redact_url_query(value: str) -> str:
    def replace(match: re.Match[str]) -> str:
        raw = match.group(0)
        parsed = urlsplit(raw)
        query = urlencode(
            [
                (key, REDACTION_MARKER if key.lower() in _SENSITIVE_QUERY_KEYS else item)
                for key, item in parse_qsl(parsed.query, keep_blank_values=True)
            ],
            doseq=True,
        )
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))

    return re.sub(r"https?://[^\s\"'<>]+", replace, value)
