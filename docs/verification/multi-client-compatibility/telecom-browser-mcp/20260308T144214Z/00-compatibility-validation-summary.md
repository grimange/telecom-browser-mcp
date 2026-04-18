# 00 - Compatibility Validation Summary

- Repository: `/home/ramjf/python-projects/telecom-browser-mcp`
- Commit: `e74a071` (working tree includes uncommitted fixes)
- Branch: `new-main`
- Validation timestamp (UTC): `2026-03-08T14:42:14Z`

## Scope Outcome
This run completed the multi-client compatibility pipeline for:
1. Codex CLI MCP environment
2. Claude Desktop MCP environment
3. OpenAI Agents SDK integration path
4. Reference MCP control harness

## Headline Result
- Discovery: `partial` overall
- Schema: `pass` overall
- Invocation: `pass` overall
- Runtime: `partial` overall

Strict host-lane transport proof passed in this run:
- `.venv` + `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1`
- `pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py`
- Result: `3 passed in 2.52s`

## Important Scope Limit
This does not establish universal multi-client runtime compatibility.
- Codex CLI and Claude Desktop still lack direct client-runtime execution evidence.
- OpenAI Agents SDK is validated through MCP transport path evidence, not a full app-level Agents runtime transcript.

## Claim Status
- Supported: schema compatibility and transport-runtime harness compatibility.
- Restricted: Codex CLI and OpenAI Agents SDK compatibility claims require scope qualifier.
- Unsupported: universal MCP compatibility claims.
