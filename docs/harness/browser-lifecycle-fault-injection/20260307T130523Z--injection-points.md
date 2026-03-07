# Injection Points Inventory (20260307T130523Z)

## Lifecycle boundaries mapped

1. Session reuse boundary
- Point: `before_session_reuse`
- Sensitivity: stale session entries with dead browser handles.

2. Context activity boundary
- Point: `after_context_created`, `before_wait_for_selector`
- Sensitivity: context closure during waits.

3. Page action boundary
- Point: `before_click`
- Sensitivity: detached page before action dispatch.

4. Selector/action boundary
- Point: `after_selector_resolved`
- Sensitivity: stale selector after DOM replacement.

5. Registry cleanup boundary
- Point: fault recovery path after classified lifecycle errors.
- Sensitivity: stale session removal and cross-session isolation.

## Mapping to code
- Injector: `src/telecom_browser_mcp/sessions/fault_injection.py`
- Boundary helpers: `tests/lifecycle/fixtures/fakes.py`
