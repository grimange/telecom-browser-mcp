# 09 Test Coverage And Gap Audit

## Coverage Strengths
- Contract envelope coverage for M1 tools is present.
- Schema/runtime parity and schema artifact drift checks are present.
- Stdio integration smoke verifies first-contact tools.
- Harness e2e validates inbound success/failure/missing control/no registration/no peer (host-gated).

## Findings
id: TC-001
title: Stdio integration smoke can skip on all exceptions, masking non-environment regressions
severity: medium
confidence: high
impacted_modules:
- tests/integration/test_stdio_smoke.py

evidence_type:
- static

evidence:
- Broad `except Exception` path converts failures to test skip.

why_it_matters:
- Protocol/registration regressions may be hidden under skip behavior.

recommended_fix:
- Restrict skip to known environment-limit error classes/messages; fail unknown exceptions.

recommended_regression_guard:
- Add negative test that unexpected exceptions are not transformed into skips.

## False Confidence Notes
- Many contract tests call `ToolService` directly and bypass MCP registration layer.
- This is useful for unit parity but should be complemented with tighter protocol-level checks.
