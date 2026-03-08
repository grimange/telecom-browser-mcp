# Static Contract Remediation Plan

- Timestamp: `20260308T094744Z`
- Pipeline: `docs/pipelines/030--remediate-static-src-contract-audit-findings.md`
- Audit input set used: `20260308T094237Z` (latest complete set in `docs/audit/src-contract-static/`)

## Ranked Queue

| Finding | File | Symbol | Severity | Fix Strategy |
|---|---|---:|---|---|
| Legacy `kwargs` envelope compatibility path can drift if unguarded | `src/telecom_browser_mcp/server/app.py` | `_normalize_legacy_kwargs`, `_validate_dispatch_kwargs`, `dispatch` | P0 | Keep strict pre-invocation validation and preserve internal-only/deprecated status for legacy envelope handling. |
| Wrapper/runtime signature drift could reappear in registration path | `src/telecom_browser_mcp/server/stdio_server.py` | `_register_tools_with_fastmcp` | P1 | Enforce canonical direct binding via static AST tests and CI guardrail checks. |
| Registration pattern bypass risk across server modules | `src/telecom_browser_mcp/server/*.py` | registration sites | P2 | Assert unique canonical registration site and direct handler binding shape. |
| Contract strictness regressions for no-arg tools | `tests/contracts`, `tests/unit` | parity/compat tests | P1 | Expand strictness checks to lock no-arg tool schema behavior and nested `kwargs` rejection. |
| CI did not enforce static disallowed-pattern checks | `.github/workflows/tool-contracts.yml` | contract jobs | P1 | Add static guardrail job running grep-based policy checks without launching MCP/browser. |
| Documentation drift risk around legacy envelope expectations | `README.md`, modernization docs | contract guidance | P3 | Keep explicit public-contract statement; document retained internal exception and protection tests. |

## Scope

- Static/remediation only.
- No MCP transport launch.
- No Playwright/browser execution.
