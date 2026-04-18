# APNTalk Modernization Review Workflow

`telecom-browser-mcp` should be used in APNTalk modernization review as an
evidence producer with explicit review boundaries.

## Review Goals

1. Confirm the adapter and contract identity used for the run.
2. Reproduce the targeted scenario with deterministic harness evidence when a
   real APNTalk runtime is not available.
3. Distinguish environment limitations from adapter drift and product/runtime
   failures using the canonical verdict summary.
4. Publish artifacts that can be compared across remediation cycles.

## Minimum Review Sequence

1. `health`
2. `capabilities`
3. `list_sessions`
4. `open_app`
5. Scenario-specific telecom tools
6. `get_peer_connection_summary` and `get_active_session_snapshot` as needed
7. `collect_debug_bundle` or failure-triggered automatic bundle capture

## Required Evidence For Review

- envelope `meta` fields:
  `contract_version`, `adapter_id`, `adapter_name`, `adapter_version`, `scenario_id`
- bundle manifest:
  `manifest.json`
- canonical verdict:
  `diagnostics/verdict_summary.json`
- runtime snapshot:
  `runtime_state/session_snapshot.json`
- HTML/screenshot capture when the runtime permits it

## Review Boundaries

- APNTalk happy-path validation is still blocked on verified selectors and runtime
  probes in this repository.
- Local host browser execution can still be environment-limited even when browser
  binaries are installed; this run observed missing `libnspr4.so` in the local
  runtime, so browser-launch failures must be treated as environment limitations
  unless reproduced in a host-capable lane.
- Fake Dialer scenarios are modernization review surrogates, not proof of APNTalk
  production parity.
