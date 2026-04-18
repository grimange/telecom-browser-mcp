# 11 - Contract Regression Watchlist

## Watch Items

### W-01: `open_app.data.ready_for_actions` must remain stable
- Type: additive compatibility field
- Regression risk: removed/renamed field breaks new clients relying on readiness gate
- Guard: `tests/contract/test_service_contracts.py:14`

### W-02: Error envelope diagnostics presence in session-broken path
- Type: semantics hardening
- Regression risk: losing diagnostics degrades machine-usable troubleshooting
- Guard: `tests/unit/test_agent_integration_remediation.py:42`

### W-03: Session operation lock safety
- Type: lifecycle safety behavior
- Regression risk: future refactors reintroduce overlapping control operations
- Guard: `tests/unit/test_agent_integration_remediation.py:11`

### W-04: SSE/HTTP entrypoint transport routing
- Type: compatibility surface
- Regression risk: wrong transport string silently breaks client integration
- Guard: `tests/integration/test_transport_entrypoints.py:14`

## Breaking-Change Watch
No mandatory breaking contract changes were introduced in this remediation run.
