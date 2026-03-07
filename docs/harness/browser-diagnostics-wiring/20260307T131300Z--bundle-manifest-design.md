# Bundle Manifest Design (20260307T131300Z)

`manifest.json` fields:

- `run_id`
- `scenario_id`
- `session_id`
- `page_id`
- `context_id`
- `fault_type`
- `injection_point`
- `status`
- `failure_classification`
- `timestamps.generated_at`
- `timestamps.timing_markers[]`
- `artifact_paths.manifest|summary|console|network|page_errors|metadata|screenshot|dom_snapshot|trace`
- `collection_gaps[]`

## Partial Capture Contract
- Missing artifacts are represented as `null` paths.
- Reason is captured in `collection_gaps`.
- Bundle validity does not depend on all artifact types being present.
