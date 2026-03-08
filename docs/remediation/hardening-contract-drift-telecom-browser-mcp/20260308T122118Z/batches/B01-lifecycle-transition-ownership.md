# B01 Lifecycle Transition Ownership

- objective: enforce explicit broken transition through session layer
- source findings: BL-001
- target files:
  - src/telecom_browser_mcp/sessions/manager.py
  - src/telecom_browser_mcp/tools/service.py
  - tests/unit/test_lifecycle_transitions.py
- acceptance: manager transition helper present and tested
- status: closed
