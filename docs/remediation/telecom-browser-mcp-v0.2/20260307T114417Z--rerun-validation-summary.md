# Rerun Validation Summary (20260307T114417Z)

## Targeted reruns executed
- Lint: `python -m ruff check src tests scripts`
- Tests: `python -m pytest -q` (9 passed)
- Interop probe: `python scripts/run_mcp_interop_probe.py`
- Tool invocation rerun: open_app + new tools + debug bundle

## Contract status changes
- fixed: 3
- partial: 2
- blocked: 0
- deferred: 3
- regressed: 0

## Key outcome
- All previously missing tool contracts are now present in the tool catalog and executable.
