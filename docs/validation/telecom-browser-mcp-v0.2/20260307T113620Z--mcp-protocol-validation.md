# MCP Protocol Validation (20260307T113620Z)

## Verdict
- Status: PARTIAL

## Evidence
- Exposed tool count: 21
- Unknown-tool path: {"ok": false, "type": "ValueError", "message": "unknown tool: unknown_tool"}
- Invalid-params path: {"ok": false, "type": "TypeError", "message": "ToolOrchestrator.open_app() missing 1 required positional argument: 'url'"}

## Gaps
- Wire-level stdio initialize/list-tools handshake not captured in this run.
