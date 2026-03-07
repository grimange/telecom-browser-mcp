# Remediation Prioritization Report

## Executive Summary
- total failures analyzed: 28
- total signatures: 5

## Top Remediation Candidates
- `SIG-004` page_closed_before_action [P0] score=75
- `SIG-005` network_failure_ui_timeout [P1] score=69
- `SIG-001` diagnostics_bundle_missing_on_failure [P1] score=65
- `SIG-003` selector_stale_after_dom_refresh [P1] score=62
- `SIG-002` javascript_runtime_error [P2] score=53

## New Regressions
- count: 2

## Known Stable Failures
- count: 3

## Environment Noise
- count: 0

## Suggested Next Pipelines
- `RB-001` P0 product_logic signatures=1
- `RB-002` P1 diagnostics_pipeline signatures=1
- `RB-003` P1 product_logic signatures=2
- `RB-004` P2 product_logic signatures=1
