# 11 - Telecom Workflow Contracts

## Workflow 1 - First Contact
1. `health({})`
2. `capabilities({})`
3. `list_sessions({})`

Expected: all return envelope with `ok=true` when service is healthy.

## Workflow 2 - Session Bring-Up
1. `open_app({ target_url, adapter_id?, headless?, session_label? })`
2. check `data.session_id`
3. check `data.ready_for_actions`

Contract rule:
- If `ready_for_actions=false`, stop telecom action chain and inspect diagnostics.

## Workflow 3 - Telecom Action Chain
1. `login_agent`
2. `wait_for_ready`
3. `wait_for_registration`
4. `wait_for_incoming_call`
5. `answer_call`

Contract rule:
- wait-state failures are structured and retryable where applicable.
- answer failures include diagnostics and artifact references.

## Workflow 4 - Inspect/Forensics/Cleanup
1. `get_active_session_snapshot`
2. `get_peer_connection_summary`
3. `collect_debug_bundle`
4. `diagnose_answer_failure`
5. `close_session`

## Evidence References
- `src/telecom_browser_mcp/server/app.py:27`
- `src/telecom_browser_mcp/tools/service.py:179`
- `src/telecom_browser_mcp/tools/service.py:214`
- `src/telecom_browser_mcp/tools/service.py:308`
- `src/telecom_browser_mcp/tools/service.py:395`
- `src/telecom_browser_mcp/models/common.py:46`
- `README.md:81`
