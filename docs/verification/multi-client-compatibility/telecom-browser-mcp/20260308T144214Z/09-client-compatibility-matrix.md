# 09 - Client Compatibility Matrix

| Client | Feasibility | Discovery | Schema | Invocation | Runtime | Evidence | Confidence | Blocker | Attribution | Workaround | Claim Status | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex CLI MCP environment | partially_observable | partial | pass | partial | unable_to_verify | static_only + observed_indirectly | medium | p1_workflow_blocker | client-specific evidence gap | run direct Codex MCP transcript validation | restricted | moderate |
| Claude Desktop MCP environment | not_accessible | unable_to_verify | pass | unable_to_verify | unable_to_verify | static_only | low | p0_hard_blocker | not_accessible | run dedicated Claude Desktop validation | unsupported | critical |
| OpenAI Agents SDK integration path | partially_observable | partial | pass | partial | partial | observed_directly | medium | p2_degraded_compatibility | app-level evidence gap | execute full Agents app integration workflow | restricted | moderate |
| Reference MCP control harness | directly_executable | pass | pass | pass | pass | observed_directly | high | none | none | none | supported | low |
