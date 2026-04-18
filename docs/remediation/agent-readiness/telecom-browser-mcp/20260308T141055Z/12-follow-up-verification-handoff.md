# 12 - Follow-Up Verification Handoff

## Required Follow-Up for B-1001 Closure
Run in a host environment with local socket + subprocess stdio permissions:

```bash
MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 \
  pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py
```

## Expected Closure Signal
- All three transport tests pass with no skips.
- Capture command output and attach to verification report.

## Additional Follow-Up
- Plan dedicated B-1002 diagnostics taxonomy normalization and conformance tests.
