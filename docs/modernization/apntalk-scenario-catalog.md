# APNTalk Modernization Scenario Catalog

This catalog maps APNTalk change areas to deterministic repo-contained scenarios,
expected tool flow, and review intent. It is designed for modernization review,
not ad hoc browser clicking.

For operator-facing release handoff, quickstart, and refusal boundaries, see
[docs/modernization/apntalk-release-handoff.md](/home/grimange/personal_projects/telecom-browser-mcp/docs/modernization/apntalk-release-handoff.md:1).

## Registration/Auth

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `apntalk-modernization-baseline` | APNTalk | bounded live UI adapter path | `login_agent` can submit the visible login form and confirm an authenticated landing page; bridge-backed `wait_for_ready` and `wait_for_registration` can succeed only when the emitted APNTalk bridge satisfies the exact bounded consumer contracts |
| `fake-dialer-happy-path` | Fake Dialer | `success`, `delayed_registration`, `registration_flapping` | `wait_for_registration` succeeds when the runtime eventually reaches `registered` |

## Supported Workflow

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `apntalk-modernization-baseline` | APNTalk | bounded bridge-backed UI workflow | the currently supported APNTalk path stays coherent end to end: bridge truth appears at `open_app`, registration and readiness waits fail closed on insufficient bridge facts, incoming ringing is observed safely, `answer_call` and `hangup_call` use only the visible main controls, and peer summary is available only while the bridge truth supports an active call |

## Inbound Signaling

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `success`, `duplicate_incoming_call`, `missing_incoming_call` | incoming-call detection is observable and classified as `call_delivery_failure` when absent |

## Answer Flow

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `apntalk-modernization-baseline` | APNTalk | bridge-backed visible-control contract | `answer_call` succeeds only when the emitted APNTalk bridge exposes a unique visible incoming-call answer control, the selector resolves uniquely, and post-click bridge facts prove a connected state; all ambiguity fails closed |
| `fake-dialer-happy-path` | Fake Dialer | `success`, `answer_fails`, `missing_answer`, `answer_mismatch` | answer success produces a connected call state; failures produce diagnostics and a debug bundle |

## Call Teardown

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `apntalk-modernization-baseline` | APNTalk | bridge-backed visible-control contract | `hangup_call` succeeds only when the emitted APNTalk bridge exposes a unique visible main-call hangup control, the selector resolves uniquely, and post-click bridge facts prove a terminal state; all ambiguity fails closed |

## UI/Store Sync

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `store_ui_divergence`, `answer_mismatch` | verdict artifacts and peer/store snapshots distinguish UI/store divergence from generic action failure |
| `apntalk-modernization-baseline` | APNTalk | bounded bridge-backed operator contract | `get_store_snapshot` remains intentionally unsupported; APNTalk operations fail closed rather than exposing raw store state |

## Reconnect/Recovery

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `reconnect_refresh_regression` | readiness or registration regressions are classified without claiming success |

## Media Path

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `connected_no_remote_audio`, `one_way_audio`, `no_peer` | peer summary captures media and connection findings for modernization triage |
