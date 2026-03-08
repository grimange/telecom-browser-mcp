# 11 - Telecom Workflow Contracts

## First Contact
1. `health({})`
2. `capabilities({})`
3. `list_sessions({})`

## Session Bring-Up
1. `open_app(...)`
2. Read `data.session_id`
3. Gate on `data.ready_for_actions`

## Session-Bound Operations
- `login_agent`, `wait_for_*`, `answer_call`, `get_peer_connection_summary`, `collect_debug_bundle`, `close_session`
- Behavior: serialized per session; lock contention returns `not_ready/session_busy` (retryable).

## Failure Forensics
- `answer_call` failure -> diagnostics + artifacts + bundle path.
- `diagnose_answer_failure` available as explicit analysis step.

## Evidence References
- `src/telecom_browser_mcp/server/app.py:27`
- `src/telecom_browser_mcp/tools/service.py:209`
- `src/telecom_browser_mcp/tools/service.py:159`
- `src/telecom_browser_mcp/tools/service.py:440`
- `src/telecom_browser_mcp/models/common.py:46`
- `README.md:85`
