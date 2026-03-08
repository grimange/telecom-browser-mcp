# B02 Evidence Redaction Expansion

- objective: widen pattern coverage for sensitive values
- source findings: DE-002
- severity: low
- target files:
  - src/telecom_browser_mcp/evidence/bundle.py
  - tests/unit/test_evidence_redaction.py
- root cause: pattern list was limited to a narrow set
- remediation:
  - add `Authorization: Bearer`, `api_key`, `secret` patterns
  - update unit tests to verify masking
- acceptance: redaction tests pass
- regression guard: keep redaction tests in required test suite
