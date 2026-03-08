# First Prioritized Run

## Executive Summary
- total failures analyzed: 3
- total signatures: 5

## Top Remediation Candidates
- selector_stale_after_dom_refresh (P2, score=52)
- page_closed_before_action (P2, score=50)
- javascript_runtime_error (P2, score=46)
- network_failure_ui_timeout (P2, score=44)
- diagnostics_bundle_missing_on_failure (P3, score=29)

## New Regressions
- count: 0

## Known Stable Failures
- count: 5

## Environment Noise
- count: 0

## Suggested Next Pipelines
- remediate product_logic P0/P1 signatures
- route diagnostics_pipeline items to diagnostics-hardening pipeline
- keep environment_or_ci items in infra triage queue
