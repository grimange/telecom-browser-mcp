# 06 Browser Lifecycle Hardening Audit

## Result
- Lifecycle transitions observed: `starting -> ready|degraded -> closing -> closed`.
- Broken browser-page gate now marks `lifecycle_state = "broken"` before returning `session_broken`.
- Browser manager cleanup logic closes context/browser/playwright in explicit order.

## Finding
id: BL-001
title: Lifecycle state machine remains partially implicit beyond broken/closed transitions
severity: low
confidence: medium
impacted_modules:
- src/telecom_browser_mcp/sessions/manager.py
- src/telecom_browser_mcp/tools/service.py

evidence_type:
- static_inference

evidence:
- `cleanup_pending` and richer terminal/intermediate states are not modeled explicitly.
- Transition ownership is split across service guard and session manager.

why_it_matters:
- Future lifecycle changes can drift if transition policy is not centralized as an explicit state machine.

recommended_fix:
- Introduce a centralized transition helper in session layer with allowed-transition checks.

recommended_regression_guard:
- Add state-transition table tests (valid and invalid transitions).
