# 09 Test Coverage And Gap Audit

## Coverage Strength
- Contract parity tests cover canonical tool map and schema drift.
- Unit redaction tests validate evidence redaction behavior.
- Integration stdio smoke verifies registration and first-contact tools.
- E2E harness scenarios exist and are host-gated.

## Finding
id: TC-002
title: Host-gated E2E scenarios are skipped in constrained environments, reducing continuous confidence
severity: informational
confidence: high
impacted_modules:
- tests/e2e/test_fake_dialer_harness.py

evidence_type:
- runtime

evidence:
- Latest run: `11 passed, 6 skipped` with all E2E tests skipped under host constraints.

why_it_matters:
- CI/sandbox runs cannot continuously validate browser-driven behavior.

recommended_fix:
- Add dedicated host-capable CI lane for `host_required` tests.

recommended_regression_guard:
- Track skip counts and fail if host lane unexpectedly skips.
