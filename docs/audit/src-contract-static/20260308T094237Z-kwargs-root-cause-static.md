# `kwargs` Root-Cause Static Audit

- Timestamp: `20260308T094237Z`
- Scope: static `src/` inspection with documentation cross-check

## `kwargs` Occurrences in `src/`

All source occurrences are in `src/telecom_browser_mcp/server/app.py` plus one defensive comment in registration code:

- `server/app.py:17-78`
- `server/stdio_server.py:57` (comment warning against synthetic wrappers)

### Occurrence Classification

| File:Line | Symbol | Snippet Role | Classification | Likely Bug Source? |
|---|---|---|---|---|
| `server/app.py:17` | `_normalize_legacy_kwargs(kwargs)` | legacy envelope normalizer entry | dispatcher-level | potential (guarded) |
| `server/app.py:19-21` | `_normalize_legacy_kwargs` | recognizes only single-key `{ "kwargs": ... }` envelope | dispatcher-level | potential (guarded) |
| `server/app.py:29-34` | `_normalize_legacy_kwargs` | rejects malformed envelope payloads with `ValueError` | dispatcher-level | no (mitigation) |
| `server/app.py:37-70` | `_validate_dispatch_kwargs` | rejects unexpected/missing fields before call | dispatcher-level | no (mitigation) |
| `server/app.py:72` | `dispatch(self, tool_name, **kwargs)` | dynamic dispatch helper signature | dispatcher-level | potential (guarded) |
| `server/app.py:78` | `dispatch` | forwards validated map via `handler(**normalized_kwargs)` | dispatcher-level | potential (guarded) |
| `server/stdio_server.py:57` | `_register_tools_with_fastmcp` comment | explicit “do not use synthetic `**kwargs` wrappers” invariant | wrapper-level | no (mitigation) |

No `kwargs` usage appears in public tool handler signatures in `tools/orchestrator.py`.

## Dangerous Spots (Current Static Reasoning)

1. `server/app.py:72-78` (`dispatch(..., **kwargs)` + forwarding)
- Still a drift-capable pattern by shape, but now guarded by `_validate_dispatch_kwargs`.

2. `server/app.py:17-34` (legacy compatibility normalizer)
- Maintains deprecated compatibility behavior; safe only while constrained to internal call sites.

## Ranked Root-Cause Candidates

1. Historical registration-wrapper drift in tool binding path (fixed in current `src`)
- File/symbol: `server/stdio_server.py` registration strategy (pre-fix wrappers, now removed)
- Confidence: **high**
- Reason: current code and tests enforce direct bound-handler registration and prohibit synthetic wrapper drift.

2. Internal helper envelope compatibility (`TelecomBrowserApp.dispatch`)
- File/symbol: `src/telecom_browser_mcp/server/app.py:17-78`
- Confidence: **medium**
- Reason: not a public MCP schema surface, but still where legacy `{ "kwargs": ... }` can enter internal calls.

3. No-arg handler incompatibility when envelopes leak
- File/symbol: e.g. `ToolOrchestrator.list_sessions` at `tools/orchestrator.py:243`
- Confidence: **high (conditional)**
- Reason: if unvalidated `kwargs` reached these handlers, Python would raise argument errors; validation now blocks this.

## Documentation Cross-Check

- `README.md:96-99` explicitly states:
  - public MCP inputs are explicit tool fields,
  - `kwargs` is not public contract input,
  - legacy envelope support is deprecated internal compatibility.
- `docs/usage/codex-agent-usage.md:26-27` recommends no-arg first-contact calls (`health`, `capabilities`, `list_sessions`).

## Static Verdict

- In current `src`, `kwargs` does not enter the canonical public FastMCP registration path.
- Remaining `kwargs` handling is confined to the internal dispatch compatibility helper and protected by strict validation.
- The prior public contract bug is statically assessed as remediated in the current source snapshot.
