# 07 - Client Compatibility Guide

| Client Pattern | Classification | Rationale |
|---|---|---|
| MCP stdio clients | Supported | first-contact smoke proven |
| Codex first-contact sequence | Supported | stdio smoke + README sequence alignment |
| MCP SSE clients | Compatible but unvalidated | transport routing tested; no live client-session smoke |
| MCP streamable HTTP clients | Compatible but unvalidated | transport routing tested; no live client-session smoke |
| Fake dialer harness consumers | Supported (test harness scope) | e2e scenario validations present |
| APNTalk real app clients | Compatible but unvalidated | adapter scaffold present; runtime selectors/paths remain limited |
| Multi-agent same-session callers | Compatible with caveats | per-session lock exists; no lock timeout/busy contract |

## Guidance
- Always run `health` -> `capabilities` -> `list_sessions` first.
- After `open_app`, inspect `data.ready_for_actions` before telecom actions.
- Treat diagnostics classifications as first-class retry/branch signals.

## Evidence References
- `tests/integration/test_stdio_smoke.py:28`
- `tests/integration/test_transport_entrypoints.py:14`
- `tests/e2e/test_fake_dialer_harness.py:34`
- `src/telecom_browser_mcp/tools/service.py:214`
- `src/telecom_browser_mcp/adapters/apntalk.py:10`
- `README.md:81`
