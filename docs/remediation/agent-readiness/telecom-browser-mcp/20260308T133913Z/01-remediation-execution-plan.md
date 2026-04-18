# 01 - Remediation Execution Plan

## Upstream Audit Input
- Selected run: `docs/agent-readiness/telecom-browser-mcp/20260308T132919Z/`
- Selection reason: newest complete readiness audit with required artifacts.
- Newer incomplete runs: none.

## Targeted Blockers
- B-901: live SSE/HTTP first-contact interoperability evidence gap.
- B-902: missing lock timeout/busy semantics.
- B-903: diagnostics taxonomy heterogeneity (P2, optional in this pass).

## Execution Strategy
1. Add root-cause lock contention semantics in service layer (shared fix across session-bound tools).
2. Add verification for lock timeout behavior.
3. Add live SSE/HTTP smoke tests with graceful environment-limitation skip policy.
4. Update docs for new lock behavior contract.

## Validation
- Command: `.venv/bin/pytest -q`
- Result: `18 passed, 8 skipped in 36.48s`

## Scope Guard
- Modified only `src/`, `tests/`, `README.md`, and remediation docs.
- No CI/deployment/infrastructure changes.
