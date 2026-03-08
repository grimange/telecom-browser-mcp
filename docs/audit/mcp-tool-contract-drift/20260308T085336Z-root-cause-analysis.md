# Root Cause Analysis — list_sessions Contract Drift

- timestamp: 2026-03-08T08:53:36Z

## Trace Path

MCP registration -> schema generation (`func_metadata`) -> wrapper callable -> tool invocation -> dispatcher/orchestrator.

## Answers Required by Phase 2

1. Who introduced `kwargs`?
- the synthetic tool wrapper pattern in `src/telecom_browser_mcp/server/stdio_server.py` (`_tool(**kwargs)`) introduced an envelope-shaped callable surface.

2. Why was it required?
- wrapper-based registration depended on signature indirection and host-specific schema extraction behavior; when this drifted, hosts exposed `kwargs` as required.

3. Was schema inferred from the wrong callable?
- yes, this was the core risk. schema fidelity depended on wrapper signature mutation rather than direct handler registration.

4. Was runtime invoked with `**payload`?
- yes, tool execution paths pass validated arguments as keyword arguments to callables.

5. Were other tools affected?
- yes. the wrapper pattern was global across all registered tools, so drift risk was shared across the full tool catalog.

## Root Cause Summary

Primary cause: wrapper indirection (`**kwargs`) plus permissive argument model strictness allowed synthetic envelope behavior to diverge from intended runtime contracts.

Secondary cause: schema strictness was not enforced (`additionalProperties` omitted), allowing invalid inputs to pass unnoticed.
