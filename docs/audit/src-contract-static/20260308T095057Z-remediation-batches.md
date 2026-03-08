# Remediation Batches (Static)

- Timestamp: `20260308T095057Z`
- Scope: follow-up hardening batches from current static findings

## Batch A — Legacy Envelope Sunset Plan

Goal: reduce long-term risk from internal compatibility-only `{ "kwargs": ... }` path.

Target files:

- `src/telecom_browser_mcp/server/app.py`
- `README.md`
- `tests/unit/test_tool_invocation_compatibility.py`

Changes:

1. Keep strict validation gate mandatory before invocation.
2. Add explicit removal/deprecation window for legacy envelope support.
3. Add/update tests for deprecation behavior if warning/telemetry is introduced.

Acceptance checks:

- No unvalidated `kwargs` map can reach handlers.
- Public docs continue to exclude `kwargs` from canonical input shape.

## Batch B — Registration Invariant Hardening

Goal: keep a single canonical registration pattern and prevent wrapper drift.

Target files:

- `src/telecom_browser_mcp/server/stdio_server.py`
- `tests/contracts/test_registration_pattern_static.py`
- `.github/workflows/tool-contracts.yml`

Changes:

1. Preserve direct binding `server.tool(name=tool_name)(handler)`.
2. Preserve static tests ensuring unique registration site and no wrapper `**kwargs` definitions.
3. Preserve CI guardrails for drift patterns.

Acceptance checks:

- CI fails if synthetic wrappers or alternate registration patterns reappear.

## Batch C — Contract Surface Consistency

Goal: keep no-arg and explicit-arg tool semantics stable across docs/code/tests.

Target files:

- `README.md`
- `docs/usage/codex-agent-usage.md`
- `tests/contracts/test_tool_contract_parity.py`

Changes:

1. Keep no-arg tools represented as empty-input schema (`health`, `list_sessions`).
2. Keep explicit-parameter tools signature-driven.
3. Keep strict `additionalProperties=false` parity checks.

Acceptance checks:

- Public contract docs and static tests remain aligned.

## Batch D — Static Guardrail Coverage Expansion

Goal: maintain static-only protection without live MCP/browser execution.

Target files:

- `scripts/check_static_contract_guardrails.sh`
- `tests/contracts/test_tool_contract_parity.py`
- `tests/contracts/test_registration_pattern_static.py`

Changes:

1. Maintain disallowed pattern checks (`tool(**kwargs)` wrappers, envelope leakage, non-canonical registration).
2. Keep parity tests for inventory, schema-signature parity, and no synthetic `kwargs` fields.
3. Emit actionable failure messages for drift diagnosis.

Acceptance checks:

- Regression suite catches contract drift in sandbox/static CI.
