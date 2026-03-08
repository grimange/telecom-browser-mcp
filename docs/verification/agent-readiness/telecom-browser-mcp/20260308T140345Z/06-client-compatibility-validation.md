# 06 - Client Compatibility Validation

## Tier Mapping Used
- Tier 1: schema discovery compatibility
- Tier 2: invocation contract compatibility
- Tier 3: observed runtime compatibility

| Client | Tier 1 | Tier 2 | Tier 3 | Compatibility Level | Evidence |
|---|---|---|---|---|---|
| Codex CLI | pass | pass | partial | invocation-compatible | tool registration + explicit first-contact flows + stdio smoke exists but skipped in this environment (`src/telecom_browser_mcp/server/app.py:19`, `tests/integration/test_stdio_smoke.py:29`, `tests/integration/test_stdio_smoke.py:59`) |
| Claude Desktop (stdio MCP) | pass | pass | partial | invocation-compatible | same stdio transport contract evidence; runtime skip due timeout in this environment (`tests/integration/test_stdio_smoke.py:59`) |
| OpenAI Agents SDK (SSE/HTTP MCP) | pass | pass | unable_to_verify | invocation-compatible | SSE/HTTP smoke tests implemented but skipped due operation-not-permitted (`tests/integration/test_http_transport_smoke.py:93`, `tests/integration/test_http_transport_smoke.py:121`) |
| Generic MCP clients | pass | pass | partial | invocation-compatible | canonical schemas + envelope tests pass; runtime depends on transport/environment (`tests/contract/test_schema_runtime_parity.py:19`, `tests/contract/test_m1_tool_envelopes.py:23`) |

## Compatibility Verdict
- Discovery and invocation compatibility are strong.
- Runtime compatibility cannot be claimed as fully verified for SSE/HTTP/stdio under current environment constraints.
