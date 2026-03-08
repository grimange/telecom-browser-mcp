# 09 - Verification Plan

## Verification Focus
- Contract and schema integrity gates.
- Transport interoperability gates (stdio + SSE + streamable-http).
- Lifecycle contention semantics gates.
- Diagnostics semantics and evidence capture gates.

## Planned Coverage
1. Keep schema parity and undeclared-field rejection tests.
2. Keep stdio first-contact smoke.
3. Keep/extend SSE and streamable-http live smoke and ensure host lane evidence capture.
4. Keep lock contention test and add more concurrent operation scenarios.
5. Add diagnostics taxonomy conformance checks once normalization is defined.

## Current Baseline
- `.venv/bin/pytest -q` => `18 passed, 8 skipped in 36.84s`.

## Evidence References
- `tests/contract/test_schema_runtime_parity.py:19`
- `tests/integration/test_stdio_smoke.py:28`
- `tests/integration/test_http_transport_smoke.py:75`
- `tests/unit/test_agent_integration_remediation.py:52`
