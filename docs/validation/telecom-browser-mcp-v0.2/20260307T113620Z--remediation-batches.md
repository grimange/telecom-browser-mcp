# Remediation Batches

## A --- contract/schema normalization
- Problem: Missing tools from explicit v0.2 catalog.
- Affected contracts: TOOL::get_environment_snapshot, TOOL::diagnose_one_way_audio, TOOL::screenshot, TOOL::collect_browser_logs
- Files: src/telecom_browser_mcp/server/stdio_server.py, src/telecom_browser_mcp/tools/orchestrator.py
- Proposed change: Add tool handlers with structured PASS/FAIL envelopes and explicit scaffold warnings where behavior is deferred.
- Required tests: contract discovery test + schema tests + harness invocation tests.
- Validation rerun: tool-contract + findings summary.

## B --- protocol fixes
- Problem: Wire-level MCP initialize/list-tools validation absent.
- Affected contracts: protocol alignment phase.
- Files: scripts/run_mcp_interop_probe.py (new), docs/validation/*
- Proposed change: Add stdio client probe script capturing initialize/tool-list traces.
- Required tests: interop smoke script in CI (optional non-blocking).
- Validation rerun: mcp-protocol-validation + interop-validation.

## C --- browser lifecycle fixes
- Problem: crash recovery and parallel session behavior not validated.
- Affected contracts: browser session lifecycle scenarios.
- Files: tests/scenarios/* (new), sessions/manager.py
- Proposed change: add deterministic session-failure injection hooks and parallel-session tests.
- Required tests: scenario tests for crash/recovery and parallel teardown.
- Validation rerun: browser-session-validation.

## D --- telecom state fixes
- Problem: flapping/duplicate/mismatch scenarios inconclusive.
- Affected contracts: telecom-flow validation scenarios.
- Files: adapters/harness.py, tests/fixtures/fake_dialer.html, tests/scenarios/*
- Proposed change: extend harness toggles for delayed/flapping/duplicate events.
- Required tests: scenario suite for registration/incoming/answer failure families.
- Validation rerun: telecom-flow-validation.

## E --- diagnostics improvements
- Problem: evidence completeness gaps (screenshots/logs/traces absent).
- Affected contracts: evidence/diagnostics validation.
- Files: evidence/*, tools/orchestrator.py
- Proposed change: implement collect_browser_logs + screenshot tool paths and enrich bundle traces.
- Required tests: artifact-presence assertions and redaction tests.
- Validation rerun: evidence-and-diagnostics-validation.

## F --- interoperability hardening
- Problem: no host-level compatibility traces with real MCP clients.
- Affected contracts: interop and protocol validation.
- Files: scripts/run_mcp_interop_probe.py, docs/guides/host-setup.md
- Proposed change: add scripted probe against at least one stdio host and one streamable-http path.
- Required tests: scripted execution artifact assertions.
- Validation rerun: interop-validation + findings-summary.
