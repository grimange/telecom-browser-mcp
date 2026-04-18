# 11 - Telecom Workflow Contracts

## Workflow A: Session Bootstrapping
1. `health({})`
2. `capabilities({})`
3. `open_app({ target_url, adapter_id?, headless?, session_label? })`
4. `list_sessions({})` (optional verification)

Contract notes:
- `open_app` returns `data.session_id` required for all session-bound tools.
- Caller must inspect `data.lifecycle_state` and diagnostics before proceeding.

## Workflow B: Agent Readiness and Registration
1. `login_agent({ session_id, credentials?, timeout_ms? })`
2. `wait_for_ready({ session_id, timeout_ms? })`
3. `wait_for_registration({ session_id, timeout_ms? })`

Contract notes:
- `wait_for_registration` failure returns `registration_not_detected`.
- `retryable=true` on timeout-like readiness failures.

## Workflow C: Incoming Call Handling
1. `wait_for_incoming_call({ session_id, timeout_ms? })`
2. `answer_call({ session_id, timeout_ms? })`
3. `get_active_session_snapshot({ session_id })`
4. `get_peer_connection_summary({ session_id })`

Contract notes:
- `answer_call` failure returns `action_failed` and includes diagnostics + artifacts + `data.bundle_path`.

## Workflow D: Forensics and Cleanup
1. `collect_debug_bundle({ session_id, reason? })`
2. `diagnose_answer_failure({ session_id })`
3. `close_session({ session_id })`

Contract notes:
- Diagnostic and evidence operations are explicitly callable independent of active failure call.

## Canonical Envelope Contract
All tools return:
- `ok`
- `tool`
- `session_id` (nullable)
- `data` object
- `error` object (nullable)
- `diagnostics` list
- `artifacts` list
- `meta.contract_version` (v1)

## Evidence References
- `src/telecom_browser_mcp/server/app.py:27`
- `src/telecom_browser_mcp/tools/service.py:122`
- `src/telecom_browser_mcp/tools/service.py:218`
- `src/telecom_browser_mcp/tools/service.py:263`
- `src/telecom_browser_mcp/tools/service.py:346`
- `src/telecom_browser_mcp/tools/service.py:395`
- `src/telecom_browser_mcp/tools/service.py:428`
- `src/telecom_browser_mcp/tools/service.py:446`
- `src/telecom_browser_mcp/models/common.py:46`
