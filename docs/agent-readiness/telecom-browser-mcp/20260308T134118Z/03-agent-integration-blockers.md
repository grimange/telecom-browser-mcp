# 03 - Agent Integration Blockers

## Current Blockers

### B-1001: Live SSE/HTTP proof remains environment-gated
- Severity: P1
- Why it blocks: transport smoke tests are present but may skip where socket operations are restricted, leaving partial runtime evidence.
- Evidence: live SSE/HTTP smoke tests include environment-limitation skip path.
- Classification: Confirmed by tests + inference.

### B-1002: Diagnostics taxonomy normalization remains incomplete
- Severity: P2
- Why it blocks: mixed diagnostic code families remain across different failure classes.
- Evidence: session_busy/session_state diagnostics coexist with answer failure taxonomy; no full normalization layer.
- Classification: Confirmed by source.

## Recently Closed Blockers
- Open-app readiness semantics ambiguity (closed via `ready_for_actions`).
- Lock contention ambiguity (closed via `not_ready/session_busy` semantics).

## Evidence References
- `src/telecom_browser_mcp/tools/service.py:159`
- `src/telecom_browser_mcp/tools/service.py:244`
- `tests/unit/test_agent_integration_remediation.py:52`
- `tests/integration/test_http_transport_smoke.py:92`
- `docs/remediation/agent-readiness/telecom-browser-mcp/20260308T133913Z/09-closure-report.md`
