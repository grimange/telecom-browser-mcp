# 08 - Remediation Backlog

## P0 (Blocking Integration)
1. Tighten `open_app` readiness semantics.
- Current issue: degraded session returned as `ok=true` can mislead orchestrators.
- Proposed: include explicit `ready_for_actions` boolean and optionally return structured error when browser page is unavailable.
- Acceptance: orchestrator can deterministically gate follow-on tool calls without probing failures.

## P1 (Stability Risks)
1. Add per-session concurrency guard.
- Implement session lock/lease model (single active mutating operation per session).
- Add tests for concurrent `wait_*`/`answer_call` calls.

2. Expand diagnostics coverage beyond answer path.
- Add diagnostic synthesis helper for browser launch, registration timeout, incoming-call timeout, and adapter-unsupported paths.
- Standardize diagnostic codes + confidence policy.

3. Validate SSE and streamable HTTP runtime paths.
- Add smoke tests equivalent to stdio first-contact.
- Add compatibility matrix updates from executed evidence.

## P2 (Ergonomics and Operability)
1. Publish operator/client workflow contract examples.
- Add request/response examples for each telecom intent tool.
- Add explicit environment limitation handling guidance.

2. Strengthen evidence bundle completeness.
- Either capture console logs or remove placeholder directory and document rationale.

3. Add per-tool output models (optional strictness improvement).
- Keep envelope stable; introduce per-tool `data` schema docs/tests.

## Evidence References
- `src/telecom_browser_mcp/tools/service.py:167`
- `src/telecom_browser_mcp/tools/service.py:178`
- `src/telecom_browser_mcp/sessions/manager.py:21`
- `src/telecom_browser_mcp/diagnostics/engine.py:7`
- `src/telecom_browser_mcp/server/sse_server.py:1`
- `src/telecom_browser_mcp/server/streamable_http_server.py:1`
- `src/telecom_browser_mcp/evidence/bundle.py:56`
- `README.md:37`
