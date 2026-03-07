# Browser Lifecycle Fault-Injection Harness Design (20260307T130523Z)

## Goal
Provide deterministic, test-only lifecycle fault injection for browser/session recovery behavior without relying on real crash events.

## Design Summary
- Injection core: `src/telecom_browser_mcp/sessions/fault_injection.py`
- Fault model execution helpers: `tests/lifecycle/fixtures/fakes.py`
- Scenario tests: `tests/lifecycle/test_*.py`
- Runner: `scripts/run_lifecycle_fault_harness.py`

## Why this shape
- Keeps production orchestration unchanged.
- Places adapter-specific behavior outside lifecycle fault simulation.
- Makes each fault trigger explicit and reproducible at named injection points.
- Produces machine-readable and markdown run artifacts for pipeline usage.
