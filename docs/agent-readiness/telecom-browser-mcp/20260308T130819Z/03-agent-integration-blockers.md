# 03 - Agent Integration Blockers

## Blocker Ledger

### B-001: Browser-open degradation is returned as `ok=true` for `open_app`
- Severity: P0
- Why it blocks: Agents can treat session creation as successful even when no browser page exists; downstream tool calls then fail with `session_broken`.
- Evidence: `open_app` always returns `_ok(...)`, even when `runtime.browser.browser_open` is false, only adding diagnostics.
- Classification: Confirmed by source.

### B-002: No explicit concurrency guard for one-active-control-per-session pattern
- Severity: P1
- Why it blocks: Multi-agent or multi-call overlap can race on the same `SessionRuntime`/Playwright page because there is no lock or lease in `SessionManager` or `ToolService`.
- Evidence: session map exists, but no lock primitives or serialized command queue around operations.
- Classification: Inferred from implementation.

### B-003: Diagnostics are strong for answer failures but narrow for broader lifecycle failures
- Severity: P1
- Why it blocks: Only selected failure paths include detailed diagnostic synthesis; other errors rely mainly on code/message/classification.
- Evidence: diagnostics engine currently centered on `diagnose_answer_failure`; other paths return minimal diagnostics.
- Classification: Confirmed by source.

### B-004: Client compatibility claims are partially unvalidated outside stdio
- Severity: P1
- Why it blocks: SSE/streamable-http entrypoints exist but no equivalent integration smoke test evidence was found in this run.
- Evidence: stdio smoke test present; no SSE/HTTP test file discovered.
- Classification: Confirmed by source/tests.

### B-005: Operator docs do not yet provide a machine-usable end-to-end contract playbook
- Severity: P2
- Why it blocks: Tool list exists, but there is no explicit request/response examples + state-machine flow doc for external client implementers.
- Evidence: README provides overview and test info, not full workflow contract examples.
- Classification: Confirmed by documentation.

## Evidence References
- `src/telecom_browser_mcp/tools/service.py:167`
- `src/telecom_browser_mcp/tools/service.py:178`
- `src/telecom_browser_mcp/tools/service.py:107`
- `src/telecom_browser_mcp/sessions/manager.py:21`
- `src/telecom_browser_mcp/diagnostics/engine.py:7`
- `src/telecom_browser_mcp/server/sse_server.py:1`
- `src/telecom_browser_mcp/server/streamable_http_server.py:1`
- `tests/integration/test_stdio_smoke.py:28`
- `README.md:5`
