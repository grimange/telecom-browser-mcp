# Batch A Protocol and Schema (20260307T123302Z)

Status: partially fixed

Rerun evidence:
- `.venv/bin/pytest -q` -> `15 passed in 0.15s`
- `.venv/bin/python scripts/run_mcp_interop_probe.py` -> timeout artifact

Result:
- schema/tool contracts remain stable
- wire-level initialize remains environment-blocked in this runtime
