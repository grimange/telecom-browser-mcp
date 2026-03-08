# 09 Test Coverage And Gap Audit

## Coverage
- Contract parity tests present and passing.
- Lifecycle and redaction unit tests present.
- Integration server bootstrap and stdio smoke tests present.
- E2E harness scenarios present but host-gated.

## Finding
id: TC-003
title: Host-gated E2E tests remain skipped in constrained environments
severity: informational
confidence: high
impacted_modules:
- tests/e2e/test_fake_dialer_harness.py

evidence_type:
- runtime

evidence:
- Latest run: `13 passed, 6 skipped` (host-required e2e skipped).

why_it_matters:
- Browser-driven behavior is not continuously validated in constrained CI/sandbox runs.

recommended_fix:
- Keep dedicated host lane and track skip/pass trends over time.

recommended_regression_guard:
- Alert when host lane has zero executed host-required tests.
