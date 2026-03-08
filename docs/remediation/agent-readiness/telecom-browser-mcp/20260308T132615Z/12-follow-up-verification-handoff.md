# 12 - Follow-up Verification Handoff

## Purpose
Hand off remaining verification work after blocker remediation.

## Required Follow-up Checks
1. Add live SSE transport smoke:
- start server in SSE mode
- initialize MCP client
- verify `health`, `capabilities`, `list_sessions` calls

2. Add live streamable-http transport smoke:
- same first-contact tool checks over streamable HTTP

3. Add concurrency stress tests:
- concurrent `wait_*` + `answer_call` on same session
- verify deterministic lock behavior and no corrupted state

4. Add diagnostics snapshot assertions:
- verify all non-answer failure classes carry meaningful diagnostics

## Recommended Next Pipeline
- `docs/pipelines/006--advanced_production_readiness_audit.md`

## Handoff Evidence
- Remediation artifacts in this run directory
- Passing suite: `17 passed, 6 skipped`
