# APNTalk Modernization Remediation Loop

Use this loop when a modernization change needs repeatable evidence:

1. Reproduce
   Run the smallest scenario from `docs/modernization/apntalk-scenario-catalog.md`
   that matches the change area.
2. Classify
   Inspect `diagnostics/verdict_summary.json` and `manifest.json` to determine
   the canonical classification and environment-vs-product domain.
3. Repair
   Change the adapter, diagnostics, harness, or CI surface needed to resolve the
   identified failure class without weakening fail-closed behavior.
4. Re-run
   Execute the narrowest relevant tests first, then rerun the scenario or
   transport lane that produced the original evidence.
5. Publish evidence
   Update the baseline corpus or attach new artifacts when the verdict changed in
   a reviewable way.

## Publishing Rules

- Do not publish a “pass” for APNTalk when the adapter still lacks verified
  selectors or runtime probes.
- Preserve the original failing evidence alongside remediation evidence.
- Prefer deterministic fake-dialer scenarios for classification drift and
  envelope/evidence regressions.
