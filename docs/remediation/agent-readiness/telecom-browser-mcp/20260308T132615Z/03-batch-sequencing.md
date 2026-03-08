# 03 - Batch Sequencing

## RB-A01 - Contract Semantics Hardening
- Blockers: B-001
- Objective: make `open_app` machine-usable for follow-on gating.
- Files changed: `src/telecom_browser_mcp/tools/service.py`, `tests/contract/test_service_contracts.py`, `README.md`
- Risk: Low (additive field)
- Completion criteria: `ready_for_actions` present and tested.

## RB-C01 - Lifecycle and Session Safety
- Blockers: B-002
- Objective: serialize session-bound operations.
- Files changed: `src/telecom_browser_mcp/sessions/manager.py`, `src/telecom_browser_mcp/tools/service.py`, `tests/unit/test_agent_integration_remediation.py`
- Risk: Medium (locking behavior)
- Completion criteria: in-flight lock blocks close; all tests pass.

## RB-D01 - Diagnostics and Error Semantics
- Blockers: B-003
- Objective: increase diagnostics coverage outside `answer_call` failure.
- Files changed: `src/telecom_browser_mcp/tools/service.py`, `tests/unit/test_agent_integration_remediation.py`
- Risk: Low
- Completion criteria: session-broken error includes state diagnostics.

## RB-E01 - Docs and Compatibility Surface
- Blockers: B-004, B-005
- Objective: strengthen transport compatibility evidence and operator clarity.
- Files changed: `tests/integration/test_transport_entrypoints.py`, `README.md`
- Risk: Low
- Completion criteria: transport entrypoint tests pass; docs updated.
