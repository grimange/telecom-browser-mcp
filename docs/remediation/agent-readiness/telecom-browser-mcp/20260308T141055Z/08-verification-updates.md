# 08 - Verification Updates

## Test Behavior Updates
- `tests/integration/test_http_transport_smoke.py`
  - added `_require_live_transport_runtime()` env gate
  - strict mode re-raises environment exceptions instead of skipping
- `tests/integration/test_stdio_smoke.py`
  - added `_require_live_transport_runtime()` env gate
  - strict mode re-raises timeout/permission limitations instead of skipping

## Commands and Results
1. Default targeted run:
- `.venv/bin/pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py tests/contract/test_m1_tool_envelopes.py tests/unit/test_agent_integration_remediation.py`
- Result: `5 passed, 3 skipped in 32.86s`

2. Strict host-proof run:
- `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 .venv/bin/pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py`
- Result in this environment: `3 failed in 30.60s` (`PermissionError: [Errno 1] Operation not permitted`, stdio timeout)

3. Full regression run:
- `.venv/bin/pytest -q`
- Result: `18 passed, 8 skipped in 36.26s`
