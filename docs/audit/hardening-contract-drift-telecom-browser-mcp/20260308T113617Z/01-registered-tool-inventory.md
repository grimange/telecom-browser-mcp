# 01 Registered Tool Inventory

## Inventory Summary
- Total registered tools: 14
- M1 canonical tools: 12
- Non-M1 support tools: 2 (`health`, `capabilities`)

## Registration Layer
- Single runtime registration location: `src/telecom_browser_mcp/server/app.py:create_mcp_server`.
- Entrypoints delegate to same factory (`stdio`, `sse`, `streamable-http`).

## Coverage Snapshot
- Contract tests: present (`tests/contract/*`).
- Integration stdio smoke: present (`tests/integration/test_stdio_smoke.py`).
- E2E harness: present (`tests/e2e/test_fake_dialer_harness.py`) with host-gated skips.

See `registered-tools.json` for full matrix.
