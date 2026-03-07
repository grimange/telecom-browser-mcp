# 11 Test Harness

## What Codex changed
- Added fake dialer fixture:
  - `tests/fixtures/fake_dialer.html`
- Added deterministic harness adapter:
  - `adapters/harness.py`
- Added unit/integration/e2e tests around harness-driven flows.

## What Codex intentionally did not change
- Did not add live PBX E2E tests in this environment.

## Tests run
- `python -m pytest -q` (8 passed)

## Evidence produced
- Harness-driven debug bundle persisted in docs audit path.

## Open risks
- Harness may not model all race conditions found in production dialers.

## Next recommended batch
- batch-09-transport-compat.md
