# 07 Inbound Call Tools

## What Codex changed
- Implemented inbound/answer/hangup tools:
  - `wait_for_incoming_call`
  - `answer_call`
  - `hangup_call`
  - `get_ui_call_state`
  - `get_active_session_snapshot`
- Added structured failure handling for incoming-call timeout and answer-flow failure.

## What Codex intentionally did not change
- Did not add complex UI retry backoff policies beyond scoped behavior.

## Tests run
- `python -m pytest -q tests/integration/test_harness_flow.py`

## Evidence produced
- Active session snapshot in debug bundle runtime files.

## Open risks
- Production reliability depends on adapter selectors/runtime mapping quality.

## Next recommended batch
- batch-05-inbound-answer-flow.md
