# 10 - Residual Risk Ledger

| Risk ID | Severity | Description | Why Residual | Recommended Next Step |
|---|---|---|---|---|
| R-01 | P1 | SSE/HTTP compatibility lacks live client-session smoke evidence | entrypoint wiring validated, but no end-to-end handshake/tool-call evidence for those transports | add transport smoke tests using MCP client over SSE/HTTP |
| R-02 | P1 | Per-session lock prevents overlap but does not define fairness/timeout policy for long operations | minimal lock introduced for safety; queue policy out of scope | introduce bounded lock wait + explicit busy error policy |
| R-03 | P2 | Diagnostics taxonomy still mixed (`session_state`, domain-specific codes, etc.) | targeted expansion only | define diagnostics schema taxonomy and normalize codes |
| R-04 | P2 | `open_app` still returns `ok=true` on degraded startup (now with `ready_for_actions=false`) | kept additive for compatibility | consider strict mode or explicit `ok=false` option in future version |

## Scope-Guard Note
These risks were discovered during remediation and are documented without expanding pipeline scope.
