# 02 - Blocker Surface Map

| Blocker ID | Severity | Affected Surface | Tool/Workflow | Upstream Evidence | Suspected Root Cause | Remediation Strategy | Target Batch | Verification Expectation | Compatibility Risk |
|---|---|---|---|---|---|---|---|---|---|
| B-1001 | P1 | Client compatibility evidence | stdio/SSE/HTTP first-contact smoke | `03-agent-integration-blockers.md`, `08-remediation-backlog.md` | environment skips hide absence of runtime proof | add strict host-lane mode that fails when runtime proof cannot be collected | RB-E01 | strict mode fails in limited env; passes in host env with permissions | Low |
| B-1002 | P2 | Diagnostics consistency | diagnostics taxonomy | `03-agent-integration-blockers.md`, `06-error-diagnostics-readiness.md` | mixed diagnostic families across paths | defer to dedicated normalization pass | RB-D02 (deferred) | taxonomy contract/test spec authored in future pass | Low |
