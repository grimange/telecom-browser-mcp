# Rerun Validation Summary (20260307T123302Z)

Commands:
- `.venv/bin/pytest -q`
- `.venv/bin/python scripts/run_mcp_interop_probe.py`

Results:
- pytest: PASS (`15 passed in 0.15s`)
- interop probe: FAIL/TIMEOUT (blocked by environment)

Status changes vs input validation:
- telecom flow: unchanged PASS
- protocol timeout: unchanged blocked
- lifecycle crash/stale-selector: unchanged deferred
- diagnostics log depth: unchanged partial
