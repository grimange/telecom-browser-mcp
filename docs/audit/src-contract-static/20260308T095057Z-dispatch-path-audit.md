# Dispatch Path Audit

- Timestamp: `20260308T095057Z`
- Scope: static call-path tracing only

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

- `src/telecom_browser_mcp/server/stdio_server.py:106-123`
- `src/telecom_browser_mcp/server/sse_server.py:8-25`
- `src/telecom_browser_mcp/server/streamable_http_server.py:8-27`
- Internal helper: `src/telecom_browser_mcp/server/app.py:72-78`

## Static Call-Path Map

### Path A: Public MCP Invocation (Canonical)

1. Transport creates `FastMCP(...)`.
2. `_register_tools_with_fastmcp(server, app)` registers each tool handler (`stdio_server.py:46-59`).
3. FastMCP invokes the registered callable directly.
4. Final callable is `ToolOrchestrator.<tool>(...)`.

Observed characteristics:

- No synthetic wrapper function in the canonical registration path.
- No local custom router forwarding raw payload maps.
- Unknown fields rejected via strict arg model (`ArgModelBase.extra = "forbid"`, `stdio_server.py:47-50`).

### Path B: Internal Programmatic Dispatch Helper

1. `TelecomBrowserApp.dispatch(tool_name, **kwargs)` (`app.py:72`).
2. Resolve target method via `getattr(self.orchestrator, tool_name, None)` (`app.py:73`).
3. Normalize optional legacy envelope (`app.py:17-34`).
4. Validate keys against handler signature (`app.py:37-70`).
5. Invoke `handler(**normalized_kwargs)` (`app.py:78`).

Observed characteristics:

- `**kwargs` is internal helper flexibility, not public MCP schema.
- Unknown or missing args are blocked before invocation.

## Static Risk Notes

- Public path is currently contract-aligned.
- Residual risk surface is limited to internal misuse of the deprecated legacy envelope compatibility branch.
