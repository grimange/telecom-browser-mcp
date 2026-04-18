# Lifecycle State Map

## Implemented States (Observed)
- `starting` (model default)
- `ready` (set in session create when browser opens)
- `degraded` (set in session create when browser cannot open)
- `closing` (set in session close)
- `closed` (set in session close)

## Transition Map
- `starting -> ready` in `SessionManager.create` when `browser_open=True`.
- `starting -> degraded` in `SessionManager.create` when browser launch fails.
- `ready|degraded -> closing -> closed` in `SessionManager.close`.

## Missing/Partial States Versus Pipeline Guidance
- `broken` exists in conceptual taxonomy but not explicitly transitioned in `SessionManager` model flow.
- No explicit `cleanup_pending` state.

## Ownership
- Browser/context/page ownership in `BrowserHandle` (`browser/manager.py`).
- Session ownership in `SessionManager` (`sessions/manager.py`).
- Tool layer requests teardown through `SessionManager.close` only.
