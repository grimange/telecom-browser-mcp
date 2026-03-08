# 07 - Doc and Compatibility Fixes

## Implemented

### DC-01: Transport entrypoint verification
Added integration tests confirming entrypoint transport wiring:
- `telecom-browser-mcp-sse` -> `transport="sse"`
- `telecom-browser-mcp-http` -> `transport="streamable-http"`

### DC-02: README workflow and compatibility guidance
README now documents:
- stdio/sse/http run commands
- `open_app.data.ready_for_actions` semantics
- first-contact tool sequence
- canonical telecom workflow sequence

## Files
- `tests/integration/test_transport_entrypoints.py:14`
- `README.md:31`
- `README.md:81`

## Verification
- Entry-point tests pass in standard suite.

## Disposition
- B-004: partially closed (wiring validated; no live SSE/HTTP session smoke yet).
- B-005: closed for current audit scope.
