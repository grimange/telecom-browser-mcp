# 06 Registration Tools

## What Codex changed
- Implemented registration tools in orchestrator:
  - `get_registration_status`
  - `wait_for_registration`
  - `assert_registered`
- Added registration diagnostics:
  - `diagnostics/registration.py`
- Added evidence capture on registration failure via bundle writer.

## What Codex intentionally did not change
- Did not implement deep app-store/SIP-runtime extraction for real adapters yet.

## Tests run
- `python -m pytest -q tests/integration/test_harness_flow.py`

## Evidence produced
- Registration runtime JSON in debug bundle path:
  - `docs/audit/telecom-browser-mcp/2026-03-07/run-20260307T112510Z/runtime/registration.json`

## Open risks
- Real-world registration truth currently depends on adapter implementation depth.

## Next recommended batch
- batch-04-registration.md
