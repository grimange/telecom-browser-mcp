# 04 - Contract Fixes

## Implemented

### CF-01: Add `open_app.data.ready_for_actions`
- Type: additive, non-breaking field.
- Purpose: explicit machine-usable gate for whether session-bound telecom actions should proceed.
- Behavior:
  - `true` when browser is open and page is available.
  - `false` when launch is degraded.
- Validation: contract test now asserts field presence and boolean type.

## Compatibility Impact
- Existing clients remain compatible (field addition only).
- New clients should prefer `ready_for_actions` over inferring readiness from `ok` alone.

## Files
- `src/telecom_browser_mcp/tools/service.py:214`
- `tests/contract/test_service_contracts.py:14`
- `README.md:48`

## Verification
- `.venv/bin/pytest -q` includes updated contract test pass.
