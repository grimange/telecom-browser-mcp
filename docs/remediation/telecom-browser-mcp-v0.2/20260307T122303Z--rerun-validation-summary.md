# Rerun Validation Summary (20260307T122303Z)

Commands:
- `.venv/bin/pytest -q`
- `.venv/bin/python scripts/run_mcp_interop_probe.py`

Results:
- pytest: PASS (`15 passed in 0.14s`)
- interop probe: FAIL/TIMEOUT, classified `blocked by environment`

Status changes vs previous validation (`20260307T121500Z`):
- telecom flow: unchanged PASS
- protocol/interop timeout: unchanged blocked
- lifecycle crash/stale-selector: unchanged deferred
- diagnostics log depth: unchanged partial
