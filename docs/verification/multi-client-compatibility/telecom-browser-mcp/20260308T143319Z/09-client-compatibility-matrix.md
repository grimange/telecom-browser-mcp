# 09 - Client Compatibility Matrix

| Client | Feasibility | Discovery | Schema | Invocation | Runtime | Evidence | Confidence | Blocker | Attribution | Workaround | Claim Status | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex CLI MCP environment | partially_observable | partial | pass | partial | unable_to_verify | static_only + test_demonstrated | medium | p1_workflow_blocker | environment limitation | Run live stdio flow in unrestricted host lane | restricted | high |
| Claude Desktop MCP environment | not_accessible | unable_to_verify | pass | unable_to_verify | unable_to_verify | static_only | low | p0_hard_blocker | not_accessible + unable_to_isolate | Execute dedicated Claude Desktop validation run | unsupported | critical |
| OpenAI Agents SDK integration path | partially_observable | partial | pass | partial | unable_to_verify | test_demonstrated + observed_indirectly | medium | p1_workflow_blocker | environment limitation | Re-run SSE/HTTP smokes with strict runtime gate on host | restricted | high |
| Reference MCP control harness | directly_executable | partial | pass | partial | unable_to_verify | observed_directly + test_demonstrated + observed_indirectly | medium | p1_workflow_blocker | environment limitation | Run harness on host where subprocess transport is permitted | restricted | moderate |
