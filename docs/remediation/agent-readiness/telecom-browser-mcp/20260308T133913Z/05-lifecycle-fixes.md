# 05 - Lifecycle Fixes

## Implemented
### LF-03: Bounded lock acquisition for all lock-guarded session operations
Replaced unbounded waits with `_acquire_operation_lock(...)` before execution in:
- `close_session`
- `login_agent`
- `wait_for_ready`
- `wait_for_registration`
- `wait_for_incoming_call`
- `answer_call`
- `get_peer_connection_summary`
- `collect_debug_bundle`

## Why
This closes the lifecycle ambiguity where operations could wait indefinitely with no machine-usable contention signal.

## Files
- `src/telecom_browser_mcp/tools/service.py:270`
- `src/telecom_browser_mcp/tools/service.py:348`
- `src/telecom_browser_mcp/tools/service.py:540`

## Verification
- Busy-semantics unit test added and passing.
