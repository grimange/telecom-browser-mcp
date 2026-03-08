# 09 - Verification Plan

## Verification Scope
- Contract integrity and schema parity.
- First-contact interoperability across transports.
- Workflow composability for telecom flows.
- Lifecycle lock guarantees and contention semantics.
- Diagnostics/error semantics for non-answer and answer failures.

## Planned Gates
1. Contract Gate
- keep schema parity + undeclared-field rejection tests.

2. Transport Gate
- keep stdio smoke.
- add live SSE smoke.
- add live streamable-http smoke.

3. Lifecycle Gate
- keep lock waiting behavior tests.
- add contention timeout/busy tests after policy is implemented.

4. Diagnostics Gate
- keep session-broken diagnostics assertions.
- add broader class coverage for timeout and adapter-unsupported diagnostics.

5. Workflow Gate
- keep fake dialer host-required scenario tests for success/failure paths.

## Current Baseline Result
- `.venv/bin/pytest -q` => `17 passed, 6 skipped in 36.17s`

## Evidence References
- `tests/contract/test_schema_runtime_parity.py:19`
- `tests/integration/test_stdio_smoke.py:28`
- `tests/integration/test_transport_entrypoints.py:14`
- `tests/unit/test_agent_integration_remediation.py:10`
- `tests/e2e/test_fake_dialer_harness.py:34`
