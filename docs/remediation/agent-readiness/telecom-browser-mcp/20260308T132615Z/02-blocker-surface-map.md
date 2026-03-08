# 02 - Blocker Surface Map

| Blocker ID | Severity | Affected Surface | Tool/Workflow | Upstream Evidence | Suspected Root Cause | Remediation Strategy | Target Batch | Verification Expectation |
|---|---|---|---|---|---|---|---|---|
| B-001 | P0 | Contract semantics | `open_app` bootstrapping | audit 03, audit 11 | success envelope lacked explicit action-readiness flag | add `data.ready_for_actions` + keep diagnostics for degraded launch | RB-A01 | contract test asserts field presence/type |
| B-002 | P1 | Lifecycle safety | session-bound tool concurrency | audit 03, audit 05 | no per-session operation serialization | add per-session `operation_lock`; apply around mutating/page operations | RB-C01 | lock-aware unit test + no regressions |
| B-003 | P1 | Diagnostics semantics | login/wait/session-broken paths | audit 03, audit 06 | diagnostics concentrated in answer-failure path | add shared session-state diagnostics helper and attach to more error paths | RB-D01 | unit test asserts diagnostics codes on broken session path |
| B-004 | P1 | Client compatibility evidence | transport entrypoints | audit 03, audit 07 | SSE/HTTP entrypoints lacked direct verification | add transport entrypoint tests asserting configured transport | RB-E01 | integration tests for sse/http entrypoints pass |
| B-005 | P2 | Operator docs | first-contact + workflow guidance | audit 03, audit 07 | docs lacked explicit machine-usable workflow narrative | update README with first-contact sequence, transport commands, readiness semantics | RB-E01 | doc section present and aligned with tool behavior |

## Notes
- B-005 is P2 and included because it directly supports B-004 compatibility clarity.
- No blocker required breaking MCP tool rename/removal.
