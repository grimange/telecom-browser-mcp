# 01 - Client Target Definition

## 1) Codex CLI MCP environment
- Client family: Codex CLI
- Environment tested: Codex workspace shell + repository harness evidence
- Transport target: stdio primarily
- Launch target: `telecom-browser-mcp-stdio` / `python -m telecom_browser_mcp`
- Runtime access: partial
- Limitation: no direct Codex MCP config-driven invocation transcript captured

## 2) Claude Desktop MCP environment
- Client family: Claude Desktop
- Environment tested: not accessible
- Transport target: stdio
- Launch target: `telecom-browser-mcp-stdio`
- Runtime access: none in this run

## 3) OpenAI Agents SDK integration path
- Client family: OpenAI Agents SDK path
- Environment tested: MCP SDK transport harness (`mcp.client.sse`, `mcp.client.streamable_http`)
- Transport target: SSE + streamable-http
- Launch target: `python -m telecom_browser_mcp.server.sse_server` / `python -m telecom_browser_mcp.server.streamable_http_server`
- Runtime access: partial (transport runtime proven; no full Agents app transcript)

## 4) Reference MCP control harness
- Client family: MCP Python SDK harness
- Environment tested: direct test execution in `.venv`
- Transports: stdio + SSE + streamable-http
- Runtime access: direct
- Limitation: none for harness itself in this run
