# 05 - Session Lifecycle Readiness

## Lifecycle Model Observed
- Session creation allocates unique session ID and artifact root.
- Lifecycle starts as `ready` when browser opens, otherwise `degraded`.
- Runtime can be marked `broken` when page becomes unavailable during tool calls.
- Close path transitions `closing` -> browser/context/playwright close -> `closed` and removes registry entry.

Status: Confirmed by source.

## Robustness Assessment
- Startup: deterministic API path, but runtime outcome depends on host/browser environment.
- Cleanup: browser/context/playwright close operations are centralized in `BrowserManager.close` and called by `SessionManager.close`.
- Failure classification: browser open failures are mapped to environment classes (`missing browser binary`, `permission blocked`, `unreachable target`, or `unknown`).

Status: Confirmed by source; runtime robustness partially unverified for real host faults in this run.

## Risks
- No explicit per-session command lock for multi-agent concurrent control.
- Degraded session can persist after successful `open_app` response.
- No automatic stale-session scavenger policy observed.

## Positive Signals
- Broken-session guard returns structured `session_broken` errors.
- Unit coverage exists for lifecycle `mark_broken` transitions.

## Evidence References
- `src/telecom_browser_mcp/sessions/manager.py:28`
- `src/telecom_browser_mcp/sessions/manager.py:75`
- `src/telecom_browser_mcp/sessions/manager.py:83`
- `src/telecom_browser_mcp/browser/manager.py:21`
- `src/telecom_browser_mcp/browser/manager.py:39`
- `src/telecom_browser_mcp/tools/service.py:107`
- `tests/unit/test_lifecycle_transitions.py:12`
