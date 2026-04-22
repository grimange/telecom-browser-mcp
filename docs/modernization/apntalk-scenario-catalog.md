# APNTalk Modernization Scenario Catalog

This catalog maps APNTalk change areas to deterministic repo-contained scenarios,
expected tool flow, and review intent. It is designed for modernization review,
not ad hoc browser clicking.

## Registration/Auth

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `apntalk-modernization-baseline` | APNTalk | bounded live UI adapter path | `login_agent` can submit the visible login form and confirm an authenticated landing page; `wait_for_ready` and `wait_for_registration` still fail closed until their selectors/runtime truth is implemented |
| `fake-dialer-happy-path` | Fake Dialer | `success`, `delayed_registration`, `registration_flapping` | `wait_for_registration` succeeds when the runtime eventually reaches `registered` |

## Inbound Signaling

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `success`, `duplicate_incoming_call`, `missing_incoming_call` | incoming-call detection is observable and classified as `call_delivery_failure` when absent |

## Answer Flow

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `success`, `answer_fails`, `missing_answer`, `answer_mismatch` | answer success produces a connected call state; failures produce diagnostics and a debug bundle |

## Call Teardown

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `apntalk-modernization-baseline` | APNTalk | adapter capabilities | hangup remains explicitly unsupported until a truthful adapter action is implemented |

## UI/Store Sync

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `store_ui_divergence`, `answer_mismatch` | verdict artifacts and peer/store snapshots distinguish UI/store divergence from generic action failure |

## Reconnect/Recovery

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `reconnect_refresh_regression` | readiness or registration regressions are classified without claiming success |

## Media Path

| Scenario ID | Target | Evidence Source | Expected Outcome |
|---|---|---|---|
| `fake-dialer-happy-path` | Fake Dialer | `connected_no_remote_audio`, `one_way_audio`, `no_peer` | peer summary captures media and connection findings for modernization triage |
