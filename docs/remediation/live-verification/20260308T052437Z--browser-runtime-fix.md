# Browser Runtime Fix

Implemented:
- Added explicit host-runtime browser failure classification:
  - `host_runtime_constraint` for sandbox-host `Operation not permitted`
  - `browser_dependency_missing` for `libnspr4.so` class failures
- Browser lifecycle stage now blocks live verification when host runtime constraints prevent launch.

Validation:
- Live rerun shows browser stage blocked with `host_runtime_constraint` instead of generic pass/fallback.

Regression coverage:
- `tests/live_verification/test_browser_runtime_classification.py`

Limitation:
- Current host still cannot launch Chromium successfully; this remains an environment blocker requiring designated host remediation.
