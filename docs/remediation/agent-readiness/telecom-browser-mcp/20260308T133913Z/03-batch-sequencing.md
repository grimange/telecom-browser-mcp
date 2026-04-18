# 03 - Batch Sequencing

## RB-C01 - Session Lock Timeout Semantics
- Blockers: B-902
- Objective: produce deterministic machine-usable busy behavior for lock contention.
- Files changed:
  - `src/telecom_browser_mcp/tools/service.py`
  - `tests/unit/test_agent_integration_remediation.py`
  - `README.md`
- Risk: Medium
- Verification: unit contention test + full suite pass.
- Completion criteria: lock timeout yields `error.code=not_ready`, `classification=session_busy`, `retryable=true`.

## RB-E01 - Live Transport Smoke Coverage
- Blockers: B-901
- Objective: add SSE/HTTP client-session first-contact smoke tests.
- Files changed:
  - `tests/integration/test_http_transport_smoke.py`
- Risk: Medium (environment sensitivity)
- Verification: tests run in capable environments; skip with explicit environment limitation when blocked.
- Completion criteria: smoke tests present, exercised, and integrated into suite.

## RB-D01 - Diagnostics Consistency Tracking
- Blockers: B-903
- Objective: track residual taxonomy inconsistency without speculative redesign.
- Files changed:
  - remediation artifacts only
- Risk: Low
- Completion criteria: residual risk + handoff contain explicit follow-up.
