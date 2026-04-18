# 02 - Blocker Surface Map

| Blocker ID | Severity | Surface | Tool/Workflow | Upstream Evidence | Root Cause | Remediation Strategy | Batch | Verification Expectation | Compatibility Risk |
|---|---|---|---|---|---|---|---|---|---|
| B-901 | P1 | Transport compatibility evidence | SSE/HTTP first-contact | audit 03 + 07 + 08 | no live client-session smoke tests for these transports | add live transport smoke tests using MCP client transports with env-aware skips | RB-E01 | tests pass when env supports local sockets; otherwise skip with explicit limitation | Low |
| B-902 | P1 | Lifecycle/session safety | session-bound operation concurrency | audit 03 + 05 + 08 | lock existed without timeout/busy semantics | add bounded lock acquisition returning structured `not_ready/session_busy` retryable errors | RB-C01 | unit test asserts busy error semantics | Medium |
| B-903 | P2 | Diagnostics consistency | error diagnostics taxonomy | audit 03 + 06 | mixed diagnostic code vocabulary | partial normalization deferred; keep ledger + policy guidance | RB-D01 | no regression in existing diagnostics tests | Low |
