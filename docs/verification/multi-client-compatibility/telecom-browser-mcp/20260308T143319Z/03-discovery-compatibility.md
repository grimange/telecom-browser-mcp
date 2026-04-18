# 03 - Discovery Compatibility

## Discovery Checks
- Server bootstrap available: pass (`tests/integration/test_server_registration.py`)
- Canonical tool registration set guarded in source: pass (`src/telecom_browser_mcp/server/app.py:75`)
- First-contact tool visibility checks implemented in stdio smoke harness: present but runtime skipped (`tests/integration/test_stdio_smoke.py:46`)
- Transport entrypoint routing (`stdio`/`sse`/`streamable-http`): pass for wiring tests (`tests/integration/test_transport_entrypoints.py`)

## Per-Client Discovery Result
| Client | Result | Evidence Type | Notes |
|---|---|---|---|
| Codex CLI | partial | static_only | Registration path exists; no direct Codex MCP discovery run captured |
| Claude Desktop | unable_to_verify | not_available | Client not accessible |
| OpenAI Agents SDK path | partial | test_demonstrated | Entrypoints and smoke harness exist; live discovery skipped by environment |
| Reference harness | partial | test_demonstrated | Bootstrap/entrypoint checks passed; live stdio/SSE/HTTP discovery skipped |
