# Scenario Catalog (20260307T130523Z)

1. Closed browser on session reuse
- Test: `tests/lifecycle/test_browser_crash_recovery.py`
- Verifies stale session detection and registry invalidation.

2. Context closes during wait
- Test: `tests/lifecycle/test_context_closure_recovery.py`
- Verifies bounded failure classification and cleanup state.

3. Page closes before action
- Test: `tests/lifecycle/test_page_detach_recovery.py`
- Verifies normalized selector/action failure with recovery attempt flag.

4. DOM replaced after selector resolution
- Test: `tests/lifecycle/test_stale_selector_recovery.py`
- Verifies stale selector normalization.

5. Parallel session isolation under lifecycle fault
- Test: `tests/lifecycle/test_parallel_session_isolation.py`
- Verifies one-session failure does not poison healthy session.
