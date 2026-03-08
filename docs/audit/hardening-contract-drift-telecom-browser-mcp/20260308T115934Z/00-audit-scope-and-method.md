# 00 Audit Scope And Method

- Timestamp: `20260308T115934Z`
- Mode: static-first, artifact-first, contract-strict
- Source pipeline: `docs/pipelines/001--static-first-hardening--contract-drift-audit.md`

## Scope Covered
- `src/telecom_browser_mcp/{server,tools,models,contracts,errors,sessions,browser,adapters,inspectors,diagnostics,evidence}`
- `tests/{contract,integration,e2e,unit}`
- `README.md`, `AGENTS.md`

## Evidence Methods
- Static source inspection with line-level references.
- Deterministic local test execution:
  - `pytest -q tests/unit tests/contract tests/integration tests/e2e`
  - result: `11 passed, 6 skipped`

## Runtime Claim Policy
- No live telecom/PBX/browser-host actions used as primary evidence.
- Runtime-style claims are based on deterministic local code/test paths.
