# 06 Browser Lifecycle Hardening Audit

## Result
- Lifecycle states in active use: `starting`, `ready`, `degraded`, `broken`, `closing`, `closed`.
- Broken browser-page path is explicit and uses `SessionManager.mark_broken(...)`.
- Cleanup ordering is explicit in browser manager.

## Finding
id: BL-003
title: State-transition policy remains distributed across service and session layers
severity: low
confidence: medium
impacted_modules:
- src/telecom_browser_mcp/tools/service.py
- src/telecom_browser_mcp/sessions/manager.py

evidence_type:
- static_inference

evidence:
- `mark_broken` now centralized, but other transitions still split between tool/session modules.

why_it_matters:
- Future lifecycle additions can drift without a unified transition policy object.

recommended_fix:
- Introduce a single transition function/table for all state changes.

recommended_regression_guard:
- Add transition-table tests covering valid/invalid edges.
