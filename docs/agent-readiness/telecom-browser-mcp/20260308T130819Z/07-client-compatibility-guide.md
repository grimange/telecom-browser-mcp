# 07 - Client Compatibility Guide

## Classification Matrix
| Client / Access Pattern | Classification | Basis |
|---|---|---|
| MCP stdio client (generic MCP client) | Supported | Integration test validates tool discovery + first-contact calls |
| Codex-style first-contact (`health`, `capabilities`, `list_sessions`) | Supported | Tool surface and stdio smoke confirm behavior |
| MCP SSE client | Compatible but unvalidated | Entrypoint exists; no direct test evidence in this run |
| MCP streamable HTTP client | Compatible but unvalidated | Entrypoint exists; no direct test evidence in this run |
| Multi-agent concurrent control on same session | Compatible but unvalidated (risk) | No lock/lease model found |
| APNTalk production dialer runtime | Compatible but unvalidated | Adapter scaffold exists; selector/runtime path hardening pending |
| Fake dialer harness client flow | Supported (test harness scope) | e2e scenarios validate intent flow |
| Non-MCP direct Python service callers | Not yet designed as public API | `ToolService` usable internally but contracts are MCP-oriented |

## Integration Guidance
- Use first-contact sequence: `health` -> `capabilities` -> `list_sessions`.
- Treat `open_app` with `lifecycle_state=degraded` and diagnostics as non-ready for telecom actions.
- Expect host/environment limitations for browser runtime; check diagnostics/classification before retry loops.
- Prefer fake-dialer adapter for deterministic CI-like contract testing.

## Evidence References
- `tests/integration/test_stdio_smoke.py:28`
- `src/telecom_browser_mcp/server/stdio_server.py:1`
- `src/telecom_browser_mcp/server/sse_server.py:1`
- `src/telecom_browser_mcp/server/streamable_http_server.py:1`
- `src/telecom_browser_mcp/tools/service.py:167`
- `src/telecom_browser_mcp/sessions/manager.py:21`
- `src/telecom_browser_mcp/adapters/apntalk.py:23`
- `tests/e2e/test_fake_dialer_harness.py:34`
