# 01 - Client Target Definition

## 1) Codex CLI MCP environment
- Client family: Codex CLI
- Concrete environment: Codex CLI workspace session (`/home/ramjf/python-projects/telecom-browser-mcp`)
- Version/build: not captured
- Operating environment: Linux (workspace sandbox)
- Transport method: expected `stdio` (primary), optional SSE/HTTP by config
- Invocation path: MCP tool discovery + tool call
- Server launch mechanism: `telecom-browser-mcp-stdio` or `python -m telecom_browser_mcp`
- Registration/config shape: MCP server registration in Codex client config (not exercised directly here)
- Runtime access level: partial
- Environmental limitations: subprocess/transport constraints observed in smoke tests
- Wrappers/shims required: none in repository evidence

## 2) Claude Desktop MCP environment
- Client family: Claude Desktop
- Concrete environment: not accessible in this run
- Version/build: unknown
- Operating environment: unknown
- Transport method: expected `stdio`
- Invocation path: desktop MCP server registration and tool invocation
- Server launch mechanism: `telecom-browser-mcp-stdio`
- Registration/config shape: desktop MCP config file format (not validated here)
- Runtime access level: none in this run
- Environmental limitations: client unavailable
- Wrappers/shims required: unknown

## 3) OpenAI Agents SDK integration path
- Client family: OpenAI Agents SDK
- Concrete environment: repository transport smoke harness (`mcp.client.sse`/`mcp.client.streamable_http`)
- Version/build: from project `.venv` dependency set (exact versions not captured in this artifact)
- Operating environment: Linux (workspace sandbox)
- Transport method: `sse`, `streamable-http`
- Invocation path: MCP client session initialize -> list/call tools
- Server launch mechanism: `python -m telecom_browser_mcp.server.sse_server` / `python -m telecom_browser_mcp.server.streamable_http_server`
- Registration/config shape: client URL-based session setup
- Runtime access level: partial (startup path present, runtime skipped)
- Environmental limitations: operation not permitted for transport smoke runtime
- Wrappers/shims required: none

## 4) Reference MCP control harness
- Client family: MCP Python SDK harness
- Concrete environment: integration/contract tests under `tests/`
- Version/build: local `.venv`
- Operating environment: Linux (workspace sandbox)
- Transport method: stdio + SSE + streamable-http (test harness coverage)
- Invocation path: `ClientSession` + `call_tool`
- Server launch mechanism: module launch (`-m telecom_browser_mcp` and transport entrypoint modules)
- Registration/config shape: `StdioServerParameters` and transport URLs
- Runtime access level: direct for contract/registration; runtime transport constrained
- Environmental limitations: stdio timeout and operation-not-permitted on live transport smoke
- Wrappers/shims required: none
