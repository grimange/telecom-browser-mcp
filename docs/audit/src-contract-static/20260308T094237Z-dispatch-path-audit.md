# Dispatch Path Audit

- Timestamp: `20260308T094237Z`
- Scope: static code-path tracing only

## Search Patterns Used

- `call_tool`
- `dispatch`
- `invoke`
- `execute`
- `router`
- `handler(`
- `**payload`
- `**kwargs`
- `payload.get("kwargs")`

## Request Entrypoints

- Stdio server bootstrap: `src/telecom_browser_mcp/server/stdio_server.py:106-123`
- SSE server bootstrap: `src/telecom_browser_mcp/server/sse_server.py:8-25`
- Streamable HTTP bootstrap: `src/telecom_browser_mcp/server/streamable_http_server.py:8-27`
- Direct internal dispatch helper: `src/telecom_browser_mcp/server/app.py:72-78`

## Static Call-Path Map

### Path A: External MCP Tool Calls (Canonical)

1. Transport startup creates `FastMCP(...)`.
2. `_register_tools_with_fastmcp(server, app)` registers each bound orchestrator method (`stdio_server.py:46-59`).
3. FastMCP dispatches client `tools/call` directly to registered handler.
4. Final handler is `ToolOrchestrator.<tool_name>(...)` (`tools/orchestrator.py`).

Observed characteristics:

- No local wrapper function between registration and orchestrator method.
- No local forwarding call using `handler(**payload)` in this canonical path.
- Strict unknown-field rejection configured globally for FastMCP arg model (`ArgModelBase` forced to `extra="forbid"` at `stdio_server.py:47-50`).

### Path B: Internal Programmatic Dispatch (Non-MCP Helper)

1. Caller invokes `TelecomBrowserApp.dispatch(tool_name, **kwargs)` (`server/app.py:72`).
2. Handler lookup via `getattr(self.orchestrator, tool_name, None)` (`server/app.py:73`).
3. Legacy envelope normalization via `_normalize_legacy_kwargs(kwargs)` (`server/app.py:17-34`).
4. Argument guard via `_validate_dispatch_kwargs(...)` (`server/app.py:37-70`).
5. Final handler invocation via `return await handler(**normalized_kwargs)` (`server/app.py:78`).

Observed characteristics:

- This path explicitly uses dynamic keyword forwarding.
- Envelope compatibility remains internal-only and guarded.
- Unknown keys and missing required keys are rejected before handler invocation.

## Invocation/Dispatch Findings by File

- `src/telecom_browser_mcp/server/stdio_server.py`
  - Registration and transport run loop only.
  - No custom local router that rewrites tool payloads.
- `src/telecom_browser_mcp/server/app.py`
  - Contains internal dispatch helper and deprecated legacy kwarg-envelope normalizer.
- `src/telecom_browser_mcp/tools/orchestrator.py`
  - Concrete tool handlers with explicit parameters; no `**kwargs` handler signatures.

## Static Risk Notes

- Canonical FastMCP path appears contract-aligned in current `src`.
- Remaining risk surface is limited to internal helper misuse, not public MCP tool schema publication.
