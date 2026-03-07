# First Run Results (20260307T130523Z)

## Commands
- `.venv/bin/pytest -q tests/lifecycle`
- `.venv/bin/python scripts/run_lifecycle_fault_harness.py`

## Outcome
- Lifecycle suite: 5 passed.
- Harness runner: 5/5 scenarios passed, 0 failed.

## Artifact outputs
- `docs/harness/browser-lifecycle-fault-injection/20260307T130523Z/lifecycle-fault-results.json`
- `docs/harness/browser-lifecycle-fault-injection/20260307T130523Z/lifecycle-fault-summary.md`

## Scenario timing snapshot
- browser_crash_recovery: 268 ms
- context_closure_recovery: 253 ms
- page_detach_recovery: 255 ms
- stale_selector_recovery: 255 ms
- parallel_session_isolation: 262 ms
