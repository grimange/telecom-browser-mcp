# 08 - Remediation Backlog

## P0
- None identified in this audit run.

## P1
1. Capture non-skipped live SSE/HTTP smoke evidence in host lane with socket permissions.
2. Decide whether lock timeout should be configurable per request/tool.

## P2
1. Normalize diagnostics taxonomy across failure classes.
2. Implement or remove `console_logs/` placeholder in evidence bundles.

## Evidence References
- `tests/integration/test_http_transport_smoke.py:92`
- `src/telecom_browser_mcp/tools/service.py:29`
- `src/telecom_browser_mcp/evidence/bundle.py:56`
- `docs/remediation/agent-readiness/telecom-browser-mcp/20260308T133913Z/10-residual-risk-ledger.md`
