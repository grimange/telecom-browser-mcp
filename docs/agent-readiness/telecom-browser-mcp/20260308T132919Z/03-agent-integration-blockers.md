# 03 - Agent Integration Blockers

## Current Blocker Ledger

### B-901: Live SSE/HTTP first-contact interoperability is not directly test-proven
- Severity: P1
- Impact: compatibility is still partly inference-based for non-stdio transports.
- Evidence: transport wiring tests exist, but no client handshake/tool-call smoke for SSE/HTTP.
- Status: Confirmed by tests/source.

### B-902: Session lock safety exists, but no explicit lock timeout/busy semantics
- Severity: P1
- Impact: long-held operations could delay other operations without machine-usable busy signaling policy.
- Evidence: per-session lock present and used; no timeout/queue policy fields in envelope.
- Status: Confirmed by source, partially inferred operational impact.

### B-903: Diagnostics taxonomy remains partially heterogeneous
- Severity: P2
- Impact: machine consumers may need additional mapping across generic vs telecom-specific diagnostic codes.
- Evidence: session-state diagnostics added; answer diagnostics are separate rule set.
- Status: Confirmed by source.

## Blockers Closed Since Prior Audit
- Prior B-001 (`open_app` readiness ambiguity) closed via `data.ready_for_actions`.
- Prior B-002 (no session operation serialization) closed via per-session `operation_lock`.
- Prior B-003 (narrow diagnostics on non-answer failures) materially improved.

## Evidence References
- `src/telecom_browser_mcp/tools/service.py:214`
- `src/telecom_browser_mcp/sessions/manager.py:20`
- `src/telecom_browser_mcp/tools/service.py:250`
- `src/telecom_browser_mcp/tools/service.py:115`
- `tests/integration/test_transport_entrypoints.py:14`
- `tests/unit/test_agent_integration_remediation.py:10`
- `docs/remediation/agent-readiness/telecom-browser-mcp/20260308T132615Z/09-closure-report.md`
