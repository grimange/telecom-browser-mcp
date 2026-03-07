# First Run Results (20260307T131300Z)

## Commands
- `.venv/bin/ruff check src tests scripts/run_lifecycle_fault_harness.py`
- `.venv/bin/pytest -q`
- `.venv/bin/python scripts/run_lifecycle_fault_harness.py --output-dir docs/harness/browser-diagnostics-wiring/20260307T131300Z-lifecycle-run`
- runtime smoke:
  - open harness session
  - `collect_browser_logs`
  - `collect_debug_bundle`

## Outcomes
- Ruff: pass.
- Pytest: `25 passed in 0.19s`.
- Lifecycle harness run: `5/5 passed` with per-scenario diagnostics manifest paths.

## Key Artifacts
- `docs/harness/browser-diagnostics-wiring/20260307T131300Z-lifecycle-run/lifecycle-fault-results.json`
- `docs/harness/browser-diagnostics-wiring/20260307T131300Z-lifecycle-run/lifecycle-fault-summary.md`
- runtime diagnostics sample root:
  - `docs/harness/browser-diagnostics-wiring/20260307T131300Z-runtime/2026-03-07/run-20260307T131314Z/browser-diagnostics/`

## Observed Behavior
- Lifecycle harness now reports diagnostics bundle references per scenario.
- Harness adapter sessions (no live Playwright runtime) produce explicit `collection_gaps` with null screenshot/DOM/trace, instead of silent omissions.
