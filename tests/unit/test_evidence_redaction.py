from telecom_browser_mcp.evidence.bundle import EvidenceCollector


def test_redact_text_masks_common_secrets() -> None:
    raw = (
        "password=abc token:xyz Authorization: Bearer abc123 cookie=foo "
        "api_key=k1 secret=s1 sip:alice@example.com"
    )
    redacted = EvidenceCollector._redact_text(raw)
    assert "abc" not in redacted
    assert "xyz" not in redacted
    assert "abc123" not in redacted
    assert "cookie=foo" not in redacted
    assert "k1" not in redacted
    assert "s1" not in redacted
    assert "sip:alice@" not in redacted
    assert "[REDACTED]" in redacted


def test_redact_obj_masks_nested_payloads() -> None:
    payload = {
        "message": "token=abc",
        "nested": [{"line": "password:xyz"}, "sip:bob@example.org"],
    }
    redacted = EvidenceCollector._redact_obj(payload)
    assert "abc" not in str(redacted)
    assert "xyz" not in str(redacted)
    assert "bob@" not in str(redacted)
