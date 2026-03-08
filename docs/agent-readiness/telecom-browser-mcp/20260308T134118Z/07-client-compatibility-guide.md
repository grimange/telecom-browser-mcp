# 07 - Client Compatibility Guide

| Client/Pattern | Classification | Basis |
|---|---|---|
| MCP stdio | Supported | live first-contact smoke validated |
| MCP SSE | Compatible but environment-gated | live smoke test exists; may skip in restricted env |
| MCP streamable-http | Compatible but environment-gated | live smoke test exists; may skip in restricted env |
| Codex first-contact sequence | Supported | tools + docs + stdio smoke |
| Fake dialer harness workflows | Supported (host-dependent) | e2e scenarios present |
| APNTalk runtime | Compatible but unvalidated | adapter scaffold and limited behavior only |
| Multi-agent same-session callers | Supported with caveat | lock semantics present; per-request lock policy not exposed |

## Evidence References
- `tests/integration/test_stdio_smoke.py:28`
- `tests/integration/test_http_transport_smoke.py:75`
- `tests/e2e/test_fake_dialer_harness.py:34`
- `src/telecom_browser_mcp/tools/service.py:159`
- `README.md:52`
