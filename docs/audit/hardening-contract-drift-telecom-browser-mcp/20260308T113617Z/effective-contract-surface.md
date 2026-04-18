# Effective Contract Surface

## Registered MCP Tools
- `health`
- `capabilities`
- `open_app`
- `list_sessions`
- `close_session`
- `login_agent`
- `wait_for_ready`
- `wait_for_registration`
- `wait_for_incoming_call`
- `answer_call`
- `get_active_session_snapshot`
- `get_peer_connection_summary`
- `collect_debug_bundle`
- `diagnose_answer_failure`

## Effective Input Behavior
- M1 tools: explicit input models (`extra=forbid`) and undeclared fields rejected as `invalid_input`.
- `list_sessions`: explicit empty input validated.
- `health`, `capabilities`: no canonical input model; zero-arg callable shape via decorator signatures.

## Effective Output Behavior
- M1 tools emit canonical envelope via `ToolResponse` (`ok/tool/session_id/data/error/diagnostics/artifacts/meta`).
- `health`, `capabilities` emit simplified non-canonical payloads.

## Error Surface
- Error codes centralized in `errors/codes.py`.
- Tool service maps invalid input to `invalid_input`, missing sessions to `session_not_found`, degraded browser page to `session_broken`.
