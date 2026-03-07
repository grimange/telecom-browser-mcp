# Batch C Telecom Flow

Changes:
- Added harness scenario controls via login `tenant` flags:
  - `registration_flapping`
  - `incoming_duplicate`
  - `answer_ui_mismatch`
- Added scenario tests covering these paths.

Rerun evidence:
- `tests/scenarios/test_telecom_scenario_injectors.py`

Status: fixed
