# 06 Browser Lifecycle Hardening Audit

## Observed Behavior
- Browser open path allocates playwright/browser/context/page.
- Failure path classifies known launch/network/sandbox errors and performs cleanup.
- Session lifecycle tracks `ready`/`degraded`/`closing`/`closed` transitions.

## Findings
id: BR-001
title: Broken session error path is not represented as explicit lifecycle state transition
severity: medium
confidence: high
impacted_modules:
- src/telecom_browser_mcp/tools/service.py
- src/telecom_browser_mcp/sessions/manager.py

evidence_type:
- static

evidence:
- `ToolService._require_browser_page` emits `session_broken` when page is unavailable.
- `SessionManager` does not set `lifecycle_state='broken'` for this condition.

why_it_matters:
- Runtime behavior and lifecycle model can diverge; analysis and remediation automation become less deterministic.

recommended_fix:
- Add explicit lifecycle transition to `broken` when page loss is detected after session creation.

recommended_regression_guard:
- Add lifecycle test asserting `session_broken` path updates model state and remains closeable/idempotent.
