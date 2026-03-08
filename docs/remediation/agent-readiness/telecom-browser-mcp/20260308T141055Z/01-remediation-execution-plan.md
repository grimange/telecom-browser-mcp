# 01 - Remediation Execution Plan

## Audit-Bound Scope
- Primary blocker targeted: B-1001 (P1).
- Secondary tracked (no implementation in this run): B-1002 (P2).

## Strategy
1. Add deterministic host-lane verification mode for transport smoke tests.
2. Keep compatibility-preserving default behavior in restricted environments.
3. Update docs so operators can collect non-skipped runtime proof.
4. Verify no contract/lifecycle regressions.

## Exclusions
- No tool contract rename/removal.
- No schema envelope changes.
- No diagnostics taxonomy redesign (B-1002 deferred).
