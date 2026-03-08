# 11 - Contract Regression Watchlist

## W-1001: Transport smoke must retain default compatibility behavior
- Type: test/runtime compatibility guard
- Risk: forcing strict failure by default would break constrained environments.
- Guard:
  - strict behavior only when `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1`
  - default behavior still skip-on-environment-limitation
- Evidence:
  - `tests/integration/test_http_transport_smoke.py:17`
  - `tests/integration/test_stdio_smoke.py:14`

## W-1002: No MCP envelope or tool signature drift in transport-proof remediation
- Type: contract stability
- Risk: accidental schema/handler drift while touching compatibility surfaces.
- Guard:
  - maintain contract test coverage and full suite checks
- Evidence:
  - `tests/contract/test_m1_tool_envelopes.py:8`
  - `.venv/bin/pytest -q` => `18 passed, 8 skipped`

## Breaking Changes
- None introduced in this run.
