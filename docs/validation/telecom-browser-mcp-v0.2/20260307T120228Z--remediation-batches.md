# Remediation Batches (20260307T120228Z)

## A --- contract/schema normalization
- Problem statement: No blocking schema mismatch found in this run.
- Affected contracts: none blocking.
- Files involved: N/A.
- Proposed change: retain current schema tests.
- Required tests: keep `tests/unit/test_models.py` and tool discovery test.
- Validation rerun scope: tool-contract-validation.

## B --- protocol fixes
- Problem statement: interop probe timed out; wire-level MCP evidence incomplete.
- Affected contracts: protocol + host interoperability.
- Files involved: `scripts/run_mcp_interop_probe.py`, `docs/guides/host-setup.md`.
- Proposed change: add richer probe diagnostics and optional longer timeout/retry strategy; capture host-side inspector transcript.
- Required tests: deterministic interop smoke in CI/local harness.
- Validation rerun scope: mcp-protocol-validation + interop-validation.

## C --- browser lifecycle fixes
- Problem statement: crash recovery and stale-selector recovery scenarios are not validated.
- Affected contracts: browser lifecycle scenarios.
- Files involved: `tests/scenarios/*`, adapter harness controls.
- Proposed change: add deterministic crash/fault injection scenarios.
- Required tests: lifecycle scenario suite additions.
- Validation rerun scope: browser-session-validation.

## D --- telecom state fixes
- Problem statement: delayed-registration and answer-timeout deterministic scenarios remain unverified.
- Affected contracts: telecom flow scenario family completeness.
- Files involved: `tests/scenarios/test_telecom_scenario_injectors.py`, `src/telecom_browser_mcp/adapters/harness.py`.
- Proposed change: add explicit delayed/timeout scenario toggles in harness.
- Required tests: scenario assertions for delayed/timeout branches.
- Validation rerun scope: telecom-flow-validation.

## E --- diagnostics improvements
- Problem statement: browser log artifacts are placeholder-level (`available: false`).
- Affected contracts: evidence-and-diagnostics usefulness.
- Files involved: `src/telecom_browser_mcp/browser/playwright_driver.py`, `src/telecom_browser_mcp/tools/orchestrator.py`.
- Proposed change: wire console/network event capture hooks and persist bounded logs.
- Required tests: diagnostics artifact completeness tests.
- Validation rerun scope: evidence-and-diagnostics-validation + failure-mode-validation.

## F --- interoperability hardening
- Problem statement: host-facing evidence is incomplete without full MCP-host transcript.
- Affected contracts: interop/readability robustness.
- Files involved: `scripts/run_mcp_interop_probe.py`, docs for host validation runbook.
- Proposed change: add host-run instructions + artifact parser for initialize/list-tools/checks.
- Required tests: host compatibility smoke record in CI docs (non-blocking if env unavailable).
- Validation rerun scope: interop-validation + findings-summary.
