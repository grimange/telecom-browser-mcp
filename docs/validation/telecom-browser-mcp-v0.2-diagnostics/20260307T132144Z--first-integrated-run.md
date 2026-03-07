# First Integrated Run

- timestamp: 20260307T132144Z
- ingested_bundles: 5
- linked_contracts: 2
- diagnostics_coverage_score: 7.14

Outputs:
- `contract-to-bundle-map.json`
- `root-cause-summary.json`
- `enriched-validation-summary.json`

Scenario coverage used in this integrated run:
- stale selector: from lifecycle diagnostics bundle `stale_selector_recovery`
- page closed/detached: from lifecycle diagnostics bundle `page_detach_recovery`
- partial bundle case: all lifecycle bundles include explicit `collection_gaps`
- javascript runtime error: validated in deterministic diagnostics test suite (`tests/lifecycle/test_browser_diagnostics_wiring.py`)
- network failure: validated in deterministic diagnostics test suite (`tests/lifecycle/test_browser_diagnostics_wiring.py`)
