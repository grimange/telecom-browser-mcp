# Scenario Coverage (20260307T131300Z)

## Required Matrix Coverage
- console capture: `tests/lifecycle/test_browser_diagnostics_wiring.py::test_console_pageerror_network_and_manifest_capture`
- page error capture: same test (pageerror assertion path)
- network failure capture: same test (`requestfailed`)
- screenshot generation: `test_screenshot_dom_and_trace_artifacts_exist`
- DOM snapshot generation: `test_screenshot_dom_and_trace_artifacts_exist`
- trace bundle generation: `test_screenshot_dom_and_trace_artifacts_exist`
- manifest integrity: `test_console_pageerror_network_and_manifest_capture`
- partial capture handling: `test_partial_capture_is_reported_when_page_closed`
- stdio-safe logging: `test_stdio_safe_collection_writes_no_stdout`
- parallel bundle isolation: `test_parallel_bundle_isolation`

## Lifecycle Harness Integration
- `scripts/run_lifecycle_fault_harness.py` now records:
  - `diagnostics_bundle_dir`
  - `diagnostics_manifest_path`
for each lifecycle scenario result.
