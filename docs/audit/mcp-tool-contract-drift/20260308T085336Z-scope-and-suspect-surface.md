# MCP Tool Contract Drift Scope and Suspect Surface

- timestamp: 2026-03-08T08:53:36Z
- scope: telecom-browser-mcp MCP tool registration, schema publication, runtime invocation
- execution mode: remediate

## Tool Surface Frozen During Repair

- frozen tool catalog size: 27
- source of truth: `src/telecom_browser_mcp/server/stdio_server.py` `TOOL_NAMES`
- freeze rule for this run: no new MCP tools added while contract repair is in progress

## Suspect Surfaces (Phase 0)

1. `src/telecom_browser_mcp/server/stdio_server.py`
- previous pattern used a synthetic wrapper `async def _tool(**kwargs)` and signature mutation.
- this pattern can drift if SDK schema extraction does not honor synthetic signature overrides.

2. `src/telecom_browser_mcp/server/app.py`
- dispatcher includes legacy payload normalization for `{"kwargs": ...}`.
- this is compatibility code and must not become the canonical public contract.

3. MCP SDK argument model behavior
- FastMCP argument models were permissive by default (`extra` not forbidden), allowing unknown fields.
- this caused strictness drift (invalid envelopes could be accepted silently).

## Initial Risk Classification

- P0: direct invocation mismatch previously observed for `list_sessions` in Codex tool host.
- P1: schema/runtime could appear aligned while permissive parsing still accepts invalid envelopes.
- P2: missing `additionalProperties: false` in published input schemas.
