# Remediation Batches (Static)

- Timestamp: `20260308T094237Z`
- Scope: contract-safe follow-up batches from current static findings

## Batch A — Dispatcher Compatibility Sunset

Goal: reduce residual internal drift surface in `TelecomBrowserApp.dispatch`.

Target files:

- `src/telecom_browser_mcp/server/app.py`
- `tests/unit/test_tool_invocation_compatibility.py`
- `README.md`

Changes:

1. Keep `_validate_dispatch_kwargs` strict gate as mandatory pre-invocation behavior.
2. Add a clear deprecation window for legacy `{ "kwargs": ... }` support and eventual removal plan.
3. Add one unit test for deprecation behavior if/when warning metadata is introduced.

Acceptance checks:

- Unknown keys never reach handlers.
- No public docs treat `kwargs` as canonical input shape.

## Batch B — Registration Invariant Lock

Goal: preserve direct signature registration and block wrapper drift regressions.

Target files:

- `src/telecom_browser_mcp/server/stdio_server.py`
- `tests/contracts/test_tool_contract_parity.py`

Changes:

1. Keep direct binding invariant (`server.tool(name=tool_name)(handler)`) and inline comment guard.
2. Keep signature parity tests ensuring registered callables match orchestrator signatures and contain no `VAR_KEYWORD` parameters.

Acceptance checks:

- CI fails if synthetic wrapper signatures are reintroduced.

## Batch C — Tool Surface Normalization

Goal: ensure internal helper semantics stay aligned with public MCP contract semantics.

Target files:

- `README.md`
- `docs/usage/codex-agent-usage.md`
- internal call sites using `app.dispatch(...)`

Changes:

1. Keep no-arg tools represented as `{}`/no args in examples.
2. Keep explicit note that legacy envelope path is deprecated internal compatibility only.
3. Ensure internal call sites use native keyword maps (`dispatch("tool", key=value)`).

Acceptance checks:

- Documentation and internal usage patterns are contract-consistent.

## Batch D — Static Contract Guard Suite

Goal: keep drift prevention static and transport-independent.

Target files:

- `tests/contracts/test_tool_contract_parity.py`
- `tests/unit/test_tool_invocation_compatibility.py`

Changes:

1. Keep strict schema tests (`additionalProperties == false`).
2. Keep synthetic-field guard (`kwargs` not present in published tool schemas).
3. Keep static registration binding and dispatch validation tests without launching MCP transports/browser.

Acceptance checks:

- Regression suite catches contract drift without runtime transport dependency.

## Execution Order

1. Batch A
2. Batch D
3. Batch B
4. Batch C

## Why This Order

- Batch A reduces remaining compatibility-only risk.
- Batch D locks behavior immediately.
- Batch B preserves public registration invariants.
- Batch C keeps docs/examples aligned with enforced behavior.
