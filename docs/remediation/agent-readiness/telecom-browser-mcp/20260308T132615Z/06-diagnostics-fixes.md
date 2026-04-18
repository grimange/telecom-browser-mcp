# 06 - Diagnostics Fixes

## Implemented

### DF-01: Shared session-state diagnostics helper
Added `_session_state_diagnostics(runtime)` with deterministic signals:
- `session_state`
- `browser_state`
- `browser_launch_error` (when present)

### DF-02: Expanded diagnostics coverage on non-answer errors
Diagnostics are now attached in additional failure paths:
- `session_closed` from `_require_runtime`
- `session_broken` from `_require_browser_page`
- `adapter_unsupported` from `login_agent`
- timeout/not-detected errors from `wait_*` tools

## Files
- `src/telecom_browser_mcp/tools/service.py:115`
- `tests/unit/test_agent_integration_remediation.py:29`

## Verification
- Added unit test asserting state diagnostics on session-broken path.
- Full test run passed.

## Non-Goals in This Batch
- Did not redesign diagnostics taxonomy globally.
- Did not add console-log capture implementation.
