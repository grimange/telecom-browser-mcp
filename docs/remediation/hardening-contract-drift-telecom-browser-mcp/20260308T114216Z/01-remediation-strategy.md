# 01 Remediation Strategy

## B01 Registry/Contract Surface Normalization
- Objective: close `CD-001` by making all registered tools canonical and envelope-stable.
- Files: contracts map, schema generator, server dispatch, tool service, contract tests.

## B02 Lifecycle Determinism Repair
- Objective: close `BR-001` by making broken-page path explicitly transition session lifecycle to `broken`.
- Files: tool service + lifecycle-focused checks.

## B03 Diagnostics/Evidence/Test Guard Hardening
- Objective: close `DE-001` and `TC-001` via redaction pipeline + stricter integration test skip policy.
- Files: evidence collector, unit redaction tests, integration skip logic.
