# 07 - Client Compatibility Guide

| Client/Pattern | Classification | Basis |
|---|---|---|
| MCP stdio clients | Supported but environment-gated | smoke exists, may skip under restrictions (`tests/integration/test_stdio_smoke.py:33`) |
| MCP SSE clients | Compatible but environment-gated | live smoke exists, may skip (`tests/integration/test_http_transport_smoke.py:80`) |
| MCP streamable-http clients | Compatible but environment-gated | live smoke exists, may skip (`tests/integration/test_http_transport_smoke.py:106`) |
| Codex first-contact sequence | Supported | tools registered + docs + smoke coverage (`README.md:87`) |
| Fake dialer harness workflows | Supported (host-dependent) | e2e harness scenarios and assertions (`tests/e2e/test_fake_dialer_harness.py:34`) |
| APNTalk runtime | Compatible but unvalidated | adapter scaffold exists, runtime selectors not fully validated in this environment |
| Multi-agent same-session callers | Supported with caveat | per-session lock + busy semantics; no per-request lock tuning (`src/telecom_browser_mcp/tools/service.py:159`) |

## Host Proof Guidance
Use strict mode for non-skipped transport proof:
`MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py`

Evidence: `README.md:109`, `tests/integration/test_stdio_smoke.py:14`, `tests/integration/test_http_transport_smoke.py:17`.
