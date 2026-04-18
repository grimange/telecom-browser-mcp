# 03 - Batch Sequencing

## RB-E01 - Host Runtime Proof Gate for Transport Smoke
- Blockers: B-1001
- Objective: make transport smoke evidence collection deterministic in host lanes.
- Files changed:
  - `tests/integration/test_http_transport_smoke.py`
  - `tests/integration/test_stdio_smoke.py`
  - `README.md`
- Risk: Low
- Verification:
  - default mode keeps skip behavior in constrained envs
  - strict mode fails on env limitations (`MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1`)
- Completion criteria: host-lane can enforce non-skipped runtime proof without changing MCP contracts.

## RB-D02 - Diagnostics Taxonomy Normalization (Deferred)
- Blockers: B-1002
- Objective: unify diagnostic taxonomy across failure classes.
- Status: deferred to avoid broad, unrelated diagnostics redesign in this run.
