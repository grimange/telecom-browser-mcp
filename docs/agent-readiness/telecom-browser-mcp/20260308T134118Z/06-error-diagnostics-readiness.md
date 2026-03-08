# 06 - Error Diagnostics Readiness

## Current State
- Stable structured error envelope is preserved.
- Session-broken and session-busy paths now provide diagnostics.
- Answer-failure diagnostics and bundle capture remain in place.

Status: Confirmed by source/tests.

## Gaps
- Full diagnostics taxonomy normalization remains pending.
- Evidence bundle still includes console-log directory placeholder without capture logic.

Status: Confirmed by source; operational impact inferred.

## Evidence References
- `src/telecom_browser_mcp/models/common.py:18`
- `src/telecom_browser_mcp/tools/service.py:117`
- `src/telecom_browser_mcp/tools/service.py:167`
- `src/telecom_browser_mcp/tools/service.py:473`
- `src/telecom_browser_mcp/evidence/bundle.py:56`
- `tests/unit/test_agent_integration_remediation.py:30`
