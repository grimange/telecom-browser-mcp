# Remaining Gaps (20260307T130523Z)

1. Real Playwright boundary hooks
- Current coverage uses deterministic fakes.
- Gap: no direct injected faults against live `PlaywrightDriver` runtime objects yet.

2. Evidence artifact depth
- Current lifecycle tests assert cleanup/classification.
- Gap: no per-scenario assertion that evidence bundles are produced on each lifecycle fault path.

3. Validation pipeline linkage
- Harness is runnable via `scripts/run_lifecycle_fault_harness.py`.
- Gap: not yet consumed automatically by existing v0.2 validation/remediation summary generation.

4. Session manager production policy
- Tests model registry invalidation behavior.
- Gap: production `SessionManager` currently marks closed sessions but does not delete them.
