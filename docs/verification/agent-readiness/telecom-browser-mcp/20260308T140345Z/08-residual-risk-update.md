# 08 - Residual Risk Update

## Risk Classification

| Risk ID | Level | Description | Evidence Basis | Mitigation |
|---|---|---|---|---|
| RR-01 | high | Runtime compatibility for SSE/HTTP/stdio first-contact remains unproven in this environment | transport smoke tests skipped (`tests/integration/test_http_transport_smoke.py:93`, `tests/integration/test_http_transport_smoke.py:121`, `tests/integration/test_stdio_smoke.py:59`) | Execute same smoke suite on host environment with required socket/stdio permissions and archive outputs |
| RR-02 | moderate | Diagnostics taxonomy heterogeneity requires consumer-side mapping | mixed classifications across session and answer diagnostics (`src/telecom_browser_mcp/tools/service.py:117`, `src/telecom_browser_mcp/diagnostics/engine.py:8`) | Implement taxonomy normalization contract and add regression tests for category mapping |
| RR-03 | low | Pipeline input path mismatch can cause audit-source confusion | expected `docs/audit/agent-readiness/...` vs actual `docs/agent-readiness/...` | Update pipeline docs to canonical path and enforce path checks in future pipelines |

## Aggregate Risk Posture
- Overall residual posture: `moderate`.
- P1 behavioral gap is environment-verification related rather than confirmed code defect.
