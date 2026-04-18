# Remediation Batches

## Batch 1
- Scope: MCP contract and startup verification hardening
- Tasks:
- Add deterministic startup checks for entrypoint and tool registration visibility
- Enforce structured error response shape checks in tests
- Exit Criteria: startup and contract checks pass in CI

## Batch 2
- Scope: Docs-to-implementation drift prevention
- Tasks:
- Add periodic drift scan against `docs/pipelines`, `docs/audit`, and implementation anchors
- Require evidence references for remediation claims
- Exit Criteria: drift report shows no high-severity mismatches

## Batch 3
- Scope: Production-readiness audit depth
- Tasks:
- Expand logging, observability, and retry/backoff audit checks
- Add operator runbook validation gate
- Exit Criteria: readiness checklist reaches PASS WITH GAPS or better
