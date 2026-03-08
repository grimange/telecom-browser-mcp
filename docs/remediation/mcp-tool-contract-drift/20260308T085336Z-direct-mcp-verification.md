# Direct MCP Verification

- timestamp: 2026-03-08T08:53:36Z
- verification artifact: `docs/remediation/mcp-tool-contract-drift/20260308T085336Z-direct-mcp-verification.json`

## Before (Observed Failure)

- external Codex MCP host observed:
  - schema required `kwargs`
  - runtime rejected `kwargs`
  - error: `ToolOrchestrator.list_sessions() got an unexpected keyword argument 'kwargs'`
- historical evidence: `docs/remediation/codex-tool-invocation-compatibility/20260308T083149Z/dispatcher-audit.md`

## After (Current Repair)

In-process FastMCP invocation path:

1. `list_sessions({})` returns success with:
- `data.count = 0`
- `data.sessions = []`

2. `list_sessions({"kwargs": {}})` now fails with strict validation:
- `Extra inputs are not permitted`

## Verification Command

`PYTHONPATH=src .venv/bin/python - <<'PY' ... FastMCP().call_tool('list_sessions', {}) ... PY`

## Environment Note

Raw stdio handshake probe remained timeout-limited in this sandbox (`startup_timeout_without_handshake`).
That transport limitation does not affect in-process FastMCP contract validation used here.
