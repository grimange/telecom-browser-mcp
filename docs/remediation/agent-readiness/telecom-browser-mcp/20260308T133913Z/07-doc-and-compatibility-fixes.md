# 07 - Doc and Compatibility Fixes

## Implemented
### DC-03: Live SSE/HTTP smoke tests
Added integration tests that:
- launch SSE and streamable-http server subprocesses
- connect via official MCP client transports
- run first-contact tool calls (`health`, `capabilities`, `list_sessions`)
- skip with explicit reason when environment blocks socket operations

### DC-04: README contract update
Documented session lock timeout behavior and expected error semantics.

## Files
- `tests/integration/test_http_transport_smoke.py:75`
- `README.md:52`

## Disposition
- B-901: partially closed in this environment (tests present; skipped when socket ops are not permitted).
