# 06 - Diagnostics Fixes

## Implemented
### DF-03: Explicit `session_busy` diagnostic
When lock acquisition times out, response includes structured diagnostic:
- `code: session_busy`
- `classification: session_busy`
- message includes timeout milliseconds
- confidence high

## Scope Note
Full diagnostics taxonomy normalization (B-903) was not completed in this batch to avoid broad refactor drift.

## Files
- `src/telecom_browser_mcp/tools/service.py:167`
- `tests/unit/test_agent_integration_remediation.py:67`

## Verification
- Busy diagnostic assertion added and passing.
