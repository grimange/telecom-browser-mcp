# 11 - Telecom Workflow Contracts

## First Contact Contract
1. `health({})`
2. `capabilities({})`
3. `list_sessions({})`

## Session Bring-Up Contract
1. `open_app(...)`
2. Read `data.session_id`
3. Gate on `data.ready_for_actions`

## Session-Bound Operations Contract
- `login_agent`, `wait_for_ready`, `wait_for_registration`, `wait_for_incoming_call`, `answer_call`, `get_peer_connection_summary`, `collect_debug_bundle`, `close_session`
- Serialized per session with lock.
- Lock contention contract: `error.code = "not_ready"`, `classification = "session_busy"`, `retryable = true`.

## Failure Forensics Contract
- `answer_call` failure returns diagnostics + artifacts and `data.bundle_path`.
- `diagnose_answer_failure` provides explicit diagnostic analysis step.

## Evidence
- `src/telecom_browser_mcp/server/app.py:19`
- `src/telecom_browser_mcp/tools/service.py:244`
- `src/telecom_browser_mcp/tools/service.py:159`
- `src/telecom_browser_mcp/tools/service.py:473`
- `README.md:85`
