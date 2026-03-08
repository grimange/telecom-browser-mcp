# 04 - Contract Fixes

## Implemented Contract Change
### CF-02: Session busy semantics for lock contention
- Added bounded operation-lock acquisition across session-bound tool operations.
- On timeout, tools return:
  - `error.code = "not_ready"`
  - `error.classification = "session_busy"`
  - `error.retryable = true`
  - diagnostics entry with `code = "session_busy"`

## Compatibility Impact
- Additive semantic clarification; no tool name or envelope break.
- Existing clients remain compatible; clients gain deterministic retry guidance on contention.

## Files
- `src/telecom_browser_mcp/tools/service.py:159`
- `README.md:52`

## Verification
- `tests/unit/test_agent_integration_remediation.py:52`
