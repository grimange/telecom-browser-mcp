# 10 - Residual Risk Ledger

| Risk ID | Severity | Description | Residual Reason | Recommended Next Step |
|---|---|---|---|---|
| R-901 | P1 | SSE/HTTP live smoke may skip in restricted environments | local socket permission limits can prevent runtime proof in CI/sandbox | run transport smoke in host lane with socket permissions and record artifacts |
| R-902 | P2 | `operation_lock_timeout_ms` is service-level, not per-request | lock policy is deterministic but not caller-tunable | add optional per-tool timeout override if needed by clients |
| R-903 | P2 | diagnostics taxonomy remains mixed beyond contention path | targeted fix only for B-902 | define taxonomy normalization contract in dedicated diagnostics pass |
