# Release Risk Register

- Date: 2026-03-08
- Project: telecom-browser-mcp

## Risks

1. `RISK-RH-001`
   - Title: Packaging prerequisites must be present in release runner
   - Severity: low
   - Release blocking: false
   - Evidence: current run has successful wheel build and wheel reinstall evidence
   - Mitigation: keep `setuptools`, `wheel`, `build` present in release runner image

2. `RISK-RH-002`
   - Title: Sandboxed stdio probe can misclassify host-ready transport
   - Severity: low
   - Release blocking: false
   - Evidence: sandbox probe timed out while escalated host probe passed (`20260308T031001Z`)
   - Mitigation: evaluate final transport readiness using intended host runtime evidence

3. `RISK-RH-003`
   - Title: Config error messaging is low-level for operator input mistakes
   - Severity: low
   - Release blocking: false
   - Evidence: raw `ValueError` string for invalid port
   - Mitigation: structured config validation and clearer user-facing messages

4. `RISK-RH-004`
   - Title: Documentation troubleshooting depth is limited
   - Severity: low
   - Release blocking: false
   - Evidence: README has notes but no dedicated hardening troubleshooting runbook
   - Mitigation: add targeted runbook entries for common environment limitations
