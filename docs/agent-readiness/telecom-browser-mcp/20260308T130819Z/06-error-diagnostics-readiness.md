# 06 - Error Diagnostics Readiness

## Error Envelope Quality
All tools return structured error data with:
- `error.code`
- `error.message`
- `error.classification`
- `error.retryable`

Status: Confirmed by source/tests.

## Error Code Coverage
Implemented error constants include:
- input/session/adapter errors
- timeout and telecom-state errors
- action/evidence/internal errors

Status: Confirmed by source.

## Diagnostic Signal Quality
- `answer_call` failure path includes synthesized diagnostics and evidence bundle artifacts.
- `diagnose_answer_failure` provides deterministic diagnosis even without a fresh failed action call.
- Redaction exists for sensitive material in evidence capture payloads.

Status: Confirmed by source/tests.

## Gaps
- No generalized diagnostic synthesis layer for every error class.
- `console_logs/` directory is created in evidence bundles but no concrete log capture write was observed.
- Diagnostics confidence is static rules-based; no cross-signal confidence calibration.

Status: Confirmed by source/inference.

## Evidence References
- `src/telecom_browser_mcp/models/common.py:18`
- `src/telecom_browser_mcp/errors/codes.py:1`
- `src/telecom_browser_mcp/tools/service.py:59`
- `src/telecom_browser_mcp/tools/service.py:374`
- `src/telecom_browser_mcp/tools/service.py:446`
- `src/telecom_browser_mcp/diagnostics/engine.py:7`
- `src/telecom_browser_mcp/evidence/bundle.py:13`
- `tests/e2e/test_fake_dialer_harness.py:56`
- `tests/unit/test_evidence_redaction.py:4`
