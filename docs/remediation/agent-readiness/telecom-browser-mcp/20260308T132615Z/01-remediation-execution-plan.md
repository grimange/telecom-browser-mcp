# 01 - Remediation Execution Plan

## Upstream Audit Selection
- Selected audit run: `docs/agent-readiness/telecom-browser-mcp/20260308T130819Z/`
- Selection basis: newest complete run with all required artifacts (00, 03-12).
- Incomplete newer run found: none.

## Scope
Audit-bound remediation for blockers from:
- `03-agent-integration-blockers.md`
- `08-remediation-backlog.md`

## Prioritized Execution
1. P0 contract/semantics hardening for `open_app` (B-001).
2. P1 lifecycle/session safety via per-session operation lock (B-002).
3. P1 diagnostics expansion on non-answer failures (B-003).
4. P1 compatibility evidence + docs upgrades (B-004, B-005 partial).

## Constraints Applied
- Preserved existing tool names and envelope structure.
- Used additive contract changes where possible.
- Limited code edits to `src/`, `tests/`, `README.md`.
- No CI or infra changes performed.

## Execution Evidence
- Validation run: `.venv/bin/pytest -q`
- Result: `17 passed, 6 skipped in 36.43s`

## Evidence References
- `docs/agent-readiness/telecom-browser-mcp/20260308T130819Z/03-agent-integration-blockers.md`
- `docs/agent-readiness/telecom-browser-mcp/20260308T130819Z/08-remediation-backlog.md`
- `src/telecom_browser_mcp/tools/service.py:179`
- `src/telecom_browser_mcp/sessions/manager.py:14`
- `tests/unit/test_agent_integration_remediation.py:10`
