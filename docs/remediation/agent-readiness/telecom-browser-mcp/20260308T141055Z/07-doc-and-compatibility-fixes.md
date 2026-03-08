# 07 - Doc and Compatibility Fixes

## Changes
- Added host-lane transport-proof instructions to README:
  - `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py`
- Documented strict-mode behavior: environment limits fail instead of skip.

## Evidence
- `README.md:109`
