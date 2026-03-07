# Batch B Browser Lifecycle (20260307T121016Z)

Status: deferred

Current evidence:
- Parallel session lifecycle test remains passing (`tests/scenarios/test_browser_lifecycle_parallel.py`).

Remaining lifecycle gaps:
- deterministic crash recovery scenario
- deterministic stale-selector recovery scenario

Reason deferred:
- Requires additional harness fault-injection surface and dedicated lifecycle fixtures beyond this remediation batch scope.
