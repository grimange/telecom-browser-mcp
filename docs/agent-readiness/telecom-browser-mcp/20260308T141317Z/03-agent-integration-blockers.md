# 03 - Agent Integration Blockers

## Current Blockers

### B-1101: Live stdio/SSE/HTTP runtime proof remains environment-gated
- Severity: P1
- Why it blocks: transport smoke tests can still be skipped in constrained environments, so release-grade runtime confidence remains conditional.
- Evidence:
  - skip handling: `tests/integration/test_stdio_smoke.py:63`, `tests/integration/test_http_transport_smoke.py:97`
  - strict host gate exists but requires host lane: `tests/integration/test_stdio_smoke.py:14`, `tests/integration/test_http_transport_smoke.py:17`
  - current run skip outputs include timeout and `Operation not permitted`.
- Classification: Confirmed by tests + runtime artifact output.

### B-1102: Diagnostics taxonomy normalization remains incomplete
- Severity: P2
- Why it blocks: diagnostics are structured but use mixed code families across session-state and answer-failure paths.
- Evidence:
  - session-state/busy diagnostics: `src/telecom_browser_mcp/tools/service.py:117`, `src/telecom_browser_mcp/tools/service.py:176`
  - answer diagnostics taxonomy: `src/telecom_browser_mcp/diagnostics/engine.py:8`
- Classification: Confirmed by source.

## Recently Closed Blockers
- Open-app readiness ambiguity closed (`ready_for_actions` present).
- Lock contention ambiguity closed (`not_ready/session_busy` semantics and tests).

## Evidence References
- `src/telecom_browser_mcp/tools/service.py:159`
- `tests/unit/test_agent_integration_remediation.py:52`
- `tests/integration/test_stdio_smoke.py:14`
- `tests/integration/test_http_transport_smoke.py:17`
