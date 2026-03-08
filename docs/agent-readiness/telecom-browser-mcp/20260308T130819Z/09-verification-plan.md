# 09 - Verification Plan

## Objectives
Design a verification suite that closes P0/P1 blockers and supports release-gate evidence for agent integration.

## Suite Structure

### V1 - Contract and Registration Gates
- Validate registered tools == canonical contracts.
- Validate schema artifacts == generated schemas.
- Validate runtime rejects undeclared fields for all tools.

### V2 - Workflow Contract Gates
- Deterministic fake-dialer scenarios for:
  - success path
  - registration missing
  - missing answer control
  - answer failure with diagnostics + bundle
- Verify state transitions and error semantics for each scenario.

### V3 - Lifecycle and Concurrency Gates
- Add async race tests for simultaneous tool calls against one `session_id`.
- Validate lock/lease behavior once implemented.
- Validate close during in-flight operation behavior.

### V4 - Diagnostics and Evidence Gates
- Assert diagnostics coverage for key non-answer failures.
- Assert redaction across nested structures and HTML snapshots.
- Assert manifest completeness and artifact capture failure reporting.

### V5 - Transport Compatibility Gates
- Add SSE first-contact smoke test.
- Add streamable-http first-contact smoke test.
- Keep stdio smoke as baseline.

## Readiness Exit Criteria
- All V1 gates pass.
- All P0-related tests pass.
- P1 gates pass or are explicitly waived with accepted risk.
- Host-required skips are tracked separately and do not mask deterministic failures.

## Existing Evidence to Reuse
- Contract parity tests.
- Envelope tests.
- Stdio first-contact integration smoke.
- Fake dialer e2e scenarios.
- Redaction and lifecycle unit tests.

## Evidence References
- `tests/contract/test_schema_runtime_parity.py:19`
- `tests/contract/test_m1_tool_envelopes.py:23`
- `tests/integration/test_stdio_smoke.py:28`
- `tests/e2e/test_fake_dialer_harness.py:34`
- `tests/unit/test_evidence_redaction.py:4`
- `tests/unit/test_lifecycle_transitions.py:12`
