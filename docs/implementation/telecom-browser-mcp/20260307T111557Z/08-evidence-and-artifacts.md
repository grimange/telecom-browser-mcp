# 08 Evidence and Artifacts

## What Codex changed
- Implemented evidence system:
  - `evidence/artifact_paths.py`
  - `evidence/screenshot_writer.py`
  - `evidence/bundle_writer.py`
  - `evidence/markdown_report.py`
  - `evidence/redaction.py`
- Implemented `collect_debug_bundle` tool.
- Persisted a real harness evidence bundle under:
  - `docs/audit/telecom-browser-mcp/2026-03-07/run-20260307T112510Z`

## What Codex intentionally did not change
- Did not implement screenshot redaction overlays yet (only payload redaction).

## Tests run
- `python -m pytest -q tests/integration/test_harness_flow.py`

## Evidence produced
- `docs/audit/telecom-browser-mcp/2026-03-07/run-20260307T112510Z/summary.json`
- `docs/audit/telecom-browser-mcp/2026-03-07/run-20260307T112510Z/report.md`
- `docs/audit/telecom-browser-mcp/2026-03-07/run-20260307T112510Z/runtime/*.json`

## Open risks
- Console/network capture is scaffold-level and should be expanded for richer forensic bundles.

## Next recommended batch
- batch-06-evidence.md
