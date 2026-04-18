# 11 Remediation Batches

## Batch HB-01 (P1)
- Goal: unify registered-tool contract surface.
- Scope: add canonical models/schemas/tests for `health` and `capabilities`.
- Maps findings: CD-001.

## Batch HB-02 (P1)
- Goal: explicit lifecycle hardening for broken state.
- Scope: state transitions, tests, deterministic close behavior after breakage.
- Maps findings: BR-001.

## Batch HB-03 (P2)
- Goal: artifact redaction safety.
- Scope: redact HTML/diagnosis artifacts and enforce tests.
- Maps findings: DE-001.

## Batch HB-04 (P2)
- Goal: reduce skip-based false confidence.
- Scope: narrow stdio skip logic to known environment constraints.
- Maps findings: TC-001.
