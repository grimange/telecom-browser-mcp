# 09 Diagnostics

## What Codex changed
- Added diagnostics modules:
  - `diagnostics/registration.py`
  - `diagnostics/incoming_call.py`
  - `diagnostics/answer_flow.py`
- Added diagnosis tools:
  - `diagnose_registration_failure`
  - `diagnose_incoming_call_failure`
  - `diagnose_answer_failure`
- Diagnostic output separates findings vs likely causes and includes next recommended tools.

## What Codex intentionally did not change
- Deferred one-way-audio diagnosis specialization as planned future scope.

## Tests run
- `python -m pytest -q tests/integration/test_diagnostics.py`

## Evidence produced
- Diagnostic payload assertions in integration tests.

## Open risks
- Cause confidence calibration is rule-based and requires field feedback.

## Next recommended batch
- batch-07-diagnostics.md
