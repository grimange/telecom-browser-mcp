# B01 Lifecycle Transition Ownership

- objective: centralize broken transition policy
- source findings: BL-001
- severity: low
- target files:
  - src/telecom_browser_mcp/sessions/manager.py
  - src/telecom_browser_mcp/tools/service.py
  - tests/unit/test_lifecycle_transitions.py
- root cause: transition assignment was directly in tool layer
- remediation:
  - add `SessionManager.mark_broken(session_id)`
  - route broken-page guard through manager method
  - add unit tests
- acceptance: transition helper exists and tests pass
- regression guard: lifecycle transition tests in unit suite
