from __future__ import annotations


def redact_payload(payload: dict) -> dict:
    redacted = {}
    for key, value in payload.items():
        if any(secret_key in key.lower() for secret_key in ("password", "token", "cookie", "auth")):
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted
