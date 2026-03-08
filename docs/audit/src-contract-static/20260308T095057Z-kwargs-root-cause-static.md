# `kwargs` Root-Cause Static Audit

- Timestamp: `20260308T095057Z`
- Scope: static `src/` inspection with documentation cross-check

## `kwargs` Occurrences in `src/`

Primary occurrences:

- `src/telecom_browser_mcp/server/app.py:17-78`
- defensive registration comment: `src/telecom_browser_mcp/server/stdio_server.py:57`

### Occurrence Classification

| File:Line | Symbol | Role | Classification | Likely Bug Source? |
|---|---|---|---|---|
| `server/app.py:17` | `_normalize_legacy_kwargs(kwargs)` | compatibility envelope entrypoint | dispatcher-level | potential (guarded) |
| `server/app.py:19-21` | `_normalize_legacy_kwargs` | recognizes `{ "kwargs": ... }` envelope | dispatcher-level | potential (guarded) |
| `server/app.py:29-34` | `_normalize_legacy_kwargs` | rejects malformed legacy payloads | dispatcher-level | no (mitigation) |
| `server/app.py:37-70` | `_validate_dispatch_kwargs` | blocks unknown/missing fields | dispatcher-level | no (mitigation) |
| `server/app.py:72` | `dispatch(..., **kwargs)` | dynamic internal dispatch signature | dispatcher-level | potential (guarded) |
| `server/app.py:78` | `dispatch` | forwards validated args | dispatcher-level | potential (guarded) |
| `server/stdio_server.py:57` | registration invariant comment | forbids synthetic wrappers in public path | wrapper-level | no (mitigation) |

No `kwargs` parameter appears in public tool handler signatures in `tools/orchestrator.py`.

## Ranked Root-Cause Candidates

1. Historical public wrapper-signature drift in registration path (fixed)
- File/symbol: `server/stdio_server.py` registration approach (previous wrapper pattern no longer present)
- Confidence: **high**
- Reason: current source binds direct handlers and includes explicit anti-wrapper invariant.

2. Internal legacy-envelope compatibility branch
- File/symbol: `src/telecom_browser_mcp/server/app.py` (`_normalize_legacy_kwargs`, `dispatch`)
- Confidence: **medium**
- Reason: still accepts deprecated compatibility shape, but now guarded by strict validation.

3. No-arg tool incompatibility if envelope leakage recurs
- File/symbol: e.g. `ToolOrchestrator.list_sessions` (`tools/orchestrator.py:243`)
- Confidence: **high (conditional)**
- Reason: no-arg handlers would reject unexpected kwargs if upstream validation regresses.

## Documentation Cross-Check

- `README.md:96-99` explicitly says `kwargs` is not a public MCP input and legacy envelope is deprecated internal compatibility.
- `docs/usage/codex-agent-usage.md:25-27` documents no-arg first-contact calls.

## Static Verdict

- `kwargs` is not currently introduced through the canonical public MCP tool contract path.
- Remaining `kwargs` behavior is internal compatibility logic in `server/app.py`, with explicit normalization and validation guards.
