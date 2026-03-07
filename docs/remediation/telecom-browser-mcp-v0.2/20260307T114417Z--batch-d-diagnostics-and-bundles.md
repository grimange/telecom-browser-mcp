# Batch D Diagnostics and Bundles (20260307T114417Z)

## Changes
- Added `collect_browser_logs` tool path writing sanitized placeholder log artifacts.
- Added `get_environment_snapshot` for explicit environment evidence.
- Added `diagnose_one_way_audio` for schema-preserving diagnostic output.

## Rerun evidence
- Harness invocation returns structured outputs and artifacts for logs.
- Existing debug bundle tooling remains functional.

## Status
- partially fixed (real browser event subscription remains future enhancement).
