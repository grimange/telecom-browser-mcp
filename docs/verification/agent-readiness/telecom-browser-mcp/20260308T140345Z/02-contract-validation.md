# 02 - Contract Validation

## Scope
Validated MCP contract invariants for schema, invocation shape, and response envelope behavior.

## Tool Interface Correctness
- Canonical input models are centralized in `CANONICAL_TOOL_INPUT_MODELS` (`src/telecom_browser_mcp/contracts/m1_contracts.py:35`).
- Server tool signatures dispatch explicit payloads (no published top-level `kwargs` envelope) (`src/telecom_browser_mcp/server/app.py:15`).
- Runtime rejects undeclared fields with deterministic `invalid_input` (`tests/contract/test_schema_runtime_parity.py:29`, `tests/contract/test_service_contracts.py:20`).
- Generated schemas match published artifacts (`tests/contract/test_schema_runtime_parity.py:19`).

Evidence tier: `test_verified` (high confidence).

## Response Envelope Invariants
Observed envelope model:
- `ok: bool`
- `data: object`
- `error: object | null`
with stable additive fields (`tool`, `session_id`, `diagnostics`, `artifacts`, `meta`).

Evidence:
- Envelope model: `src/telecom_browser_mcp/models/common.py:46`
- Cross-tool envelope assertions: `tests/contract/test_m1_tool_envelopes.py:8`
- Error path with structured code: `tests/contract/test_m1_tool_envelopes.py:77`

Evidence tier: `test_verified` (high confidence).

## Error Semantics
- Error shape is stable via `ToolError` (`src/telecom_browser_mcp/models/common.py:18`).
- Busy contention semantics are deterministic (`not_ready`, `classification=session_busy`, `retryable=true`) (`src/telecom_browser_mcp/tools/service.py:167`).
- Missing session error remains stable (`session_not_found`) (`tests/contract/test_m1_tool_envelopes.py:99`).

Evidence tier: `test_verified` (high confidence).

## Contract Verdict
- No contract regression detected in evaluated scope.
- Contract closure for B-902 is validated.
