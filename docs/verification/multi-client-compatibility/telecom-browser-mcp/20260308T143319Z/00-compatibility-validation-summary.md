# 00 - Compatibility Validation Summary

- Repository: `/home/ramjf/python-projects/telecom-browser-mcp`
- Commit: `e74a071`
- Branch: `new-main`
- Validation timestamp (UTC): `2026-03-08T14:33:19Z`

## Scope Outcome
This run completed the multi-client compatibility pipeline for:
1. Codex CLI MCP environment
2. Claude Desktop MCP environment
3. OpenAI Agents SDK integration path
4. Reference MCP control harness

## Headline Result
- Discovery: `partial` overall
- Schema: `pass` overall
- Invocation: `partial` overall
- Runtime: `unable_to_verify` overall

Runtime compatibility could not be claimed for any client in this environment because transport smoke checks were skipped due environment limits:
- stdio timeout
- SSE operation not permitted
- streamable-http operation not permitted

## Evidence Used
- Direct execution (`.venv`):
  - `pytest -q tests/contract/test_m1_tool_envelopes.py tests/contract/test_schema_runtime_parity.py` -> `4 passed`
  - `pytest -q tests/integration/test_server_registration.py tests/integration/test_transport_entrypoints.py` -> `3 passed`
  - `pytest -q -rs tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py` -> `3 skipped`
- Source/static evidence:
  - Tool registration and dispatch: `src/telecom_browser_mcp/server/app.py`
  - Canonical contract map: `src/telecom_browser_mcp/contracts/m1_contracts.py`
  - Published schemas: `docs/contracts/m1/*.schema.json`

## Claim Status
- Allowed: "Schema compatibility is strong and contract drift checks are passing."
- Restricted: "Codex CLI/Claude/OpenAI Agents runtime compatibility" (requires host runtime proof).
- Unsupported: "Works with all MCP clients" and any universal compatibility statement.
