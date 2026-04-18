# 08 - Remediation Backlog

## P0
- None currently identified in this run.

## P1
1. Add live SSE first-contact smoke using MCP client session.
- Target: convert SSE status from compatible-unvalidated to supported.

2. Add live streamable HTTP first-contact smoke using MCP client session.
- Target: convert streamable-http status from compatible-unvalidated to supported.

3. Define lock timeout/busy semantics for session lock contention.
- Target: deterministic client behavior under contention.

## P2
1. Normalize diagnostics taxonomy across failure families.
2. Decide and implement console log capture policy in evidence bundle (capture or remove placeholder).

## Evidence References
- `tests/integration/test_transport_entrypoints.py:14`
- `src/telecom_browser_mcp/tools/service.py:250`
- `src/telecom_browser_mcp/evidence/bundle.py:56`
- `docs/remediation/agent-readiness/telecom-browser-mcp/20260308T132615Z/10-residual-risk-ledger.md`
