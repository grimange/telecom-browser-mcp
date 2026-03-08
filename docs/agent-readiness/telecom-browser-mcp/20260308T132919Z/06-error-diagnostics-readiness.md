# 06 - Error Diagnostics Readiness

## Envelope and Error Structure
- Error envelope remains stable and structured (`code/message/classification/retryable`).
- Error responses include diagnostics list consistently.

Status: Confirmed by source/tests.

## Diagnostics Improvements Observed
- Added reusable session-state diagnostics for non-answer failure paths.
- `session_broken` path includes state/context diagnostics.
- `answer_call` failure still emits diagnosis + evidence bundle.

Status: Confirmed by source/tests.

## Remaining Gaps
- Diagnostics taxonomy still mixed between generic and domain-specific codes.
- Evidence collector still creates `console_logs/` directory without captured logs in current implementation.

Status: Confirmed by source; operational impact inferred.

## Evidence References
- `src/telecom_browser_mcp/models/common.py:18`
- `src/telecom_browser_mcp/tools/service.py:115`
- `src/telecom_browser_mcp/tools/service.py:141`
- `src/telecom_browser_mcp/tools/service.py:395`
- `src/telecom_browser_mcp/diagnostics/engine.py:7`
- `src/telecom_browser_mcp/evidence/bundle.py:56`
- `tests/unit/test_agent_integration_remediation.py:30`
- `tests/e2e/test_fake_dialer_harness.py:56`
