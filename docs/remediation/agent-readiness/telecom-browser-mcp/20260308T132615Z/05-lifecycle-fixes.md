# 05 - Lifecycle Fixes

## Implemented

### LF-01: Per-session operation lock
- Added `operation_lock` to `SessionRuntime`.
- Applied lock around session-bound operations that manipulate/read browser runtime state:
  - `close_session`
  - `login_agent`
  - `wait_for_ready`
  - `wait_for_registration`
  - `wait_for_incoming_call`
  - `answer_call`
  - `get_peer_connection_summary`
  - `collect_debug_bundle`

### LF-02: Close path respects in-flight operation
- `close_session` now acquires session lock before close.

## Files
- `src/telecom_browser_mcp/sessions/manager.py:14`
- `src/telecom_browser_mcp/tools/service.py:240`
- `tests/unit/test_agent_integration_remediation.py:10`

## Verification
- Added lock behavior test proving close waits while lock is held.
- Full test run passed.

## Remaining Lifecycle Limits
- No global queue/fairness policy beyond per-session lock.
