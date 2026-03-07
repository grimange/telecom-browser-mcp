# Batch D Diagnostics and Bundles

Changes:
- `screenshot` now produces deterministic artifact in no-browser harness environments.
- `answer_call` now surfaces explicit warning when UI/store state mismatches.
- `collect_browser_logs` remains structured with explicit availability notes.

Status: fixed (contract-level), with implementation-depth caveat retained for full browser event capture.
