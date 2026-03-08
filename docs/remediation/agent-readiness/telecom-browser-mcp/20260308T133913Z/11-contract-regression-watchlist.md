# 11 - Contract Regression Watchlist

## Watch Items

### W-11-01: Busy contention error semantics
- Expected on lock timeout:
  - `error.code = not_ready`
  - `error.classification = session_busy`
  - `error.retryable = true`
- Guard: `tests/unit/test_agent_integration_remediation.py:52`

### W-11-02: `open_app.data.ready_for_actions`
- Must remain present and boolean.
- Guard: `tests/contract/test_service_contracts.py:14`

### W-11-03: Transport first-contact smoke behavior
- SSE/HTTP tests should keep validating client handshake/tool calls where environment permits.
- Guard: `tests/integration/test_http_transport_smoke.py:75`

## Breaking Change Record
- No breaking MCP contract changes in this run.
