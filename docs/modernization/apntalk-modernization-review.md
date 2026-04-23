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
- Phase 0 APNTalk truth fields in `capabilities`, `open_app`, or
  `get_active_session_snapshot`:
  `support_status`, `capability_truth`, `phase0_observation.runtime_bridge`,
  `phase0_observation.contract_observations`
- consumer-side bridge contract reference:
  `docs/apntalk-runtime-bridge-contract.md`
- bundle manifest:
  `manifest.json`
- canonical verdict:
  `diagnostics/verdict_summary.json`
- runtime snapshot:
  `runtime_state/session_snapshot.json`
- HTML/screenshot capture when the runtime permits it

## Review Boundaries

- APNTalk login-path validation is implemented with visible-UI selectors and
  conservative post-login confirmation. When APNTalk exposes a valid runtime
  bridge, this repo can now support bridge-backed `get_registration_status`,
  `wait_for_registration`, `wait_for_ready`, `wait_for_incoming_call`, and
  `get_peer_connection_summary` with bounded observation-only semantics, plus
  bounded `answer_call` and `hangup_call` only when the bridge exposes the
  visible main softphone controls, those selectors resolve uniquely, and the
  required post-click transitions are observed. Store snapshot validation
  remains blocked in this repository.
- Phase 0 diagnostics are observation-only. Runtime bridge presence, selector
  observations, and microphone permission hints do not upgrade APNTalk support
  claims beyond the currently implemented `login_ui_plus_bridge_observation`
  corridor.
- A `bridge_valid` verdict only means the page exposed the expected bounded
  consumer contract. It does not, by itself, prove answer, store
  snapshot, media permission, audio playout success, or control affordances in
  this repo.
- Local host browser execution can still be environment-limited even when browser
  binaries are installed; this run observed missing `libnspr4.so` in the local
  runtime, so browser-launch failures must be treated as environment limitations
  unless reproduced in a host-capable lane.
- Fake Dialer scenarios are modernization review surrogates, not proof of APNTalk
  production parity.
