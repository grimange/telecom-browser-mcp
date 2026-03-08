# 09 - Verification Plan

## Focus Areas
1. Contract integrity and schema/runtime parity.
2. First-contact transport interoperability (stdio/SSE/HTTP).
3. Session lifecycle contention safety.
4. Diagnostics semantics and artifact capture behavior.

## Planned Verification Assets
- Keep schema parity and undeclared-field rejection tests.
- Keep canonical envelope tests for all tools.
- Run transport smoke in default and strict host mode.
- Keep contention tests and add scenarios as needed.
- Add diagnostics taxonomy conformance tests after taxonomy is defined.

## Baseline Results (This Run)
- `.venv/bin/pytest -q` -> `18 passed, 8 skipped in 36.67s`
- transport/e2e skip report captured with `-rs`.

## Evidence
- `tests/contract/test_schema_runtime_parity.py:19`
- `tests/contract/test_m1_tool_envelopes.py:23`
- `tests/integration/test_stdio_smoke.py:33`
- `tests/integration/test_http_transport_smoke.py:80`
- `tests/unit/test_agent_integration_remediation.py:52`
