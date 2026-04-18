# 08 - Verification Updates

## New/Updated Tests
- Updated: `tests/contract/test_service_contracts.py`
  - validates `open_app.data.ready_for_actions` exists and is boolean.

- Added: `tests/unit/test_agent_integration_remediation.py`
  - verifies close waits on in-flight session lock.
  - verifies session-broken errors include expanded diagnostics.

- Added: `tests/integration/test_transport_entrypoints.py`
  - verifies SSE and streamable-http entrypoint transport settings.

## Validation Run
- Command: `.venv/bin/pytest -q`
- Result: `17 passed, 6 skipped in 36.43s`

## Mapping to Blockers
- B-001: covered by contract test.
- B-002: covered by lock unit test.
- B-003: covered by diagnostics unit test.
- B-004: covered by transport entrypoint integration tests.
