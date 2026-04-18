# 08 - Remediation Backlog

## P0
- None identified in this run.

## P1
1. Capture passing strict host-lane transport evidence for stdio/SSE/HTTP.
   - Why: B-1101 remains unresolved in this restricted environment.

## P2
1. Normalize diagnostics taxonomy across session-state and answer-failure classes.
2. Implement real console log capture or remove placeholder directory from bundles.

## Evidence
- `tests/integration/test_stdio_smoke.py:14`
- `tests/integration/test_http_transport_smoke.py:17`
- `src/telecom_browser_mcp/diagnostics/engine.py:8`
- `src/telecom_browser_mcp/evidence/bundle.py:56`
