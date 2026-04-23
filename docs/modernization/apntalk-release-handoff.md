# APNTalk Bounded Workflow Release Handoff

This handoff summarizes the current release-ready APNTalk MCP workflow. It is
operator guidance, not a feature expansion.

## Support At A Glance

Current support status: `login_ui_plus_bridge_observation`.

The APNTalk adapter supports the following bounded workflow when APNTalk emits a
valid `window.__apnTalkTestBridge` matching bridge version `1.4.0`:

1. `open_app` reports APNTalk adapter identity, capability truth, and bridge
   diagnostics.
2. `login_agent` uses the visible APNTalk login form and conservative
   post-login confirmation.
3. `get_registration_status` and `wait_for_registration` use bridge-backed
   registration facts only.
4. `wait_for_ready` succeeds only on the exact bridge-backed ready semantics.
5. `wait_for_incoming_call` observes only safe unambiguous incoming ringing.
6. `answer_call` clicks only the unique visible main answer control and requires
   bridge-backed connected transition evidence.
7. `get_peer_connection_summary` returns only the bounded bridge-backed active
   peer-connection summary.
8. `hangup_call` clicks only the unique visible main hangup control and requires
   bridge-backed terminal transition evidence.

`get_store_snapshot` remains intentionally unsupported.

## Operator Quickstart

1. Register and start `telecom-browser-mcp` using the stdio setup in
   [docs/setup/codex-mcp.md](/home/grimange/personal_projects/telecom-browser-mcp/docs/setup/codex-mcp.md:1).
2. Configure `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for the intended APNTalk host
   before calling `open_app`.
3. Call `capabilities` and confirm APNTalk reports
   `login_ui_plus_bridge_observation`.
4. Call `open_app` for the APNTalk URL and inspect
   `phase0_observation.runtime_bridge.validation_verdict`.
5. Proceed through the supported workflow only when bridge diagnostics and
   capability truth show the relevant live detection or selector binding.
6. If a call step fails closed, inspect `get_active_session_snapshot` before
   retrying or changing APNTalk product assumptions.

## Known Limits And Refusal Boundaries

- Absent, malformed, partial, or version-mismatched bridges fail closed.
- Bridge presence alone is never enough to mark a tool successful.
- `wait_for_ready` is not equivalent to page load or authentication alone.
- `wait_for_incoming_call` does not prove answerability.
- `answer_call` and `hangup_call` are visible-UI actions only; there are no
  backend shortcuts or hidden mutation methods.
- Selector ambiguity, hidden controls, disabled controls, or missing post-click
  transitions fail closed.
- `get_peer_connection_summary` does not expose SDP, ICE candidates, device
  labels, media permission success, or audio playout success.
- `get_store_snapshot` remains unsupported until a separate bounded redacted
  APNTalk snapshot contract is implemented and tested.

## Verification Evidence

The bounded APNTalk workflow is protected by:

- adapter contract tests for bridge validation, readiness, registration,
  incoming-call, peer-connection, answer, and hangup paths
- service-level APNTalk workflow coverage that exercises the supported sequence
  across bridge-backed transitions
- registry and service contract tests that preserve capability truth and keep
  `get_store_snapshot` unbound

Recommended release checks for this handoff:

```bash
pytest -q tests/unit/test_apntalk_contract.py tests/unit/test_tool_service_phase0.py tests/unit/test_adapter_registry.py tests/contract/test_service_contracts.py
ruff check README.md docs/usage/codex-agent-usage.md docs/modernization/apntalk-scenario-catalog.md docs/modernization/apntalk-release-handoff.md
```

## Change Summary

- APNTalk is packaged for bounded operation around the existing bridge-backed
  observation and visible-control workflow.
- Operator guidance is centered on bridge version `1.4.0`, fail-closed
  diagnostics, and visible UI controls.
- No new MCP capabilities are introduced by this handoff.
