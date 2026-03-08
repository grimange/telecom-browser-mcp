# Dispatcher Audit

## Scope

Audit path:

Codex MCP request -> FastMCP tool wrapper -> app dispatcher -> orchestrator method

Files audited:

- `src/telecom_browser_mcp/server/stdio_server.py`
- `src/telecom_browser_mcp/server/app.py`
- `src/telecom_browser_mcp/tools/orchestrator.py`

## Exact mismatch location (pre-fix)

- Wrapper registration used `async def _tool(**kwargs)` (`stdio_server.py`, pre-fix line around `_make_tool`).
- FastMCP inferred a synthetic argument surface that external clients exposed as a single `kwargs` field.
- Dispatcher forwarded payload as `handler(**kwargs)` (`app.py`), which passed `kwargs=...` into methods like `list_sessions(self)`.
- Runtime failure observed: `ToolOrchestrator.list_sessions() got an unexpected keyword argument 'kwargs'`.

## Fix implemented

1. Signature alignment at registration:
- `src/telecom_browser_mcp/server/stdio_server.py:45-63`
- Wrapper now sets `__signature__` from the bound orchestrator method (`inspect.signature(handler)`), so schema discovery reflects real tool parameters.

2. Backward-compatible dispatcher normalization:
- `src/telecom_browser_mcp/server/app.py:15-39`
- Added `_normalize_legacy_kwargs` to unwrap legacy payloads when the request shape is exactly `{ "kwargs": <dict-or-json-string> }`.

3. Safe no-arg tools added for first-contact invocation:
- `src/telecom_browser_mcp/tools/orchestrator.py:51-95`
- Added `health()` and `capabilities(include_groups: bool = True)`.
- Added both tools to `TOOL_NAMES` in `stdio_server.py:14-42`.

## Post-fix dispatcher flow

Codex request payload -> signature-aligned wrapper -> normalized kwargs (legacy-compatible) -> orchestrator method invocation.

No synthetic `kwargs` forwarding remains in the canonical path.

## Residual risk

Local stdio client probe inside this sandbox failed during subprocess bootstrap (`ModuleNotFoundError: anyio`), so wire-level validation remained environment-limited. In-process dispatcher smoke and unit tests were used for deterministic verification.
