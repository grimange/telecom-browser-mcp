# telecom-browser-mcp Improvement Plan for APNTalk Modernization — Revised

## Objective

Strengthen `telecom-browser-mcp` as a governance-safe, fail-closed, UI-truthful browser companion for APNTalk modernization.

This revised plan preserves the original direction — **observation first, mutation later** — while tightening the parts that would otherwise drift or become ambiguous in live APNTalk use:

- the APNTalk runtime bridge must become a versioned contract, not an ad hoc hook,
- readiness and registration must use precise state semantics,
- store inspection must be bounded and redacted,
- diagnostics must arrive earlier in the rollout,
- DOM and runtime disagreement must fail closed,
- declared support must be separated from live-session availability.

This plan is for **browser-edge observation and bounded UI interaction**. It does **not** replace APNTalk backend authority, provider authority, or telephony-core governance.

---

## Executive Summary

The current fit remains **PARTIAL_FIT**.

`telecom-browser-mcp` already has value for APNTalk login smoke and bounded browser-side evidence collection, but it is not yet a trustworthy control or observability surface for readiness, SIP registration, incoming-call truth, answer, hangup, or peer-connection diagnostics unless APNTalk-specific bindings are made explicit and testable.

The key improvement is not “more browser automation.” The key improvement is a **small, explicit, read-only APNTalk contract surface** that allows the MCP layer to observe meaningful UI/runtime truth without guessing.

The rollout should remain staged:

1. make the pilot path reliable and diagnosable,
2. define and test the APNTalk bridge contract,
3. add bounded read-only observation,
4. add incoming-call truth,
5. add answer/hangup only after state observation is stable,
6. defer richer in-call controls.

---

## Scope Boundary

### In Scope

- APNTalk login through the visible UI
- read-only observation of browser/runtime state
- bounded answer/hangup through visible UI controls
- browser-side WebRTC evidence collection
- APNTalk-specific diagnostics for private/VPN environments
- repeatable operator scenario packs

### Explicitly Out of Scope

This plan does **not**:

- replace APNTalk backend authority,
- replace PBX/provider command or event authority,
- create a hidden control plane outside the visible APNTalk UI,
- claim telephony-core closure for APNTalk modernization,
- broaden to DTMF, mute, hold, conference, or outbound dialing before the bounded pilot succeeds.

---

## Revised Governing Principles

### 1. Visible UI for mutation

Mutating actions must happen through visible APNTalk controls. No hidden browser shortcuts should be treated as product truth.

### 2. Read-only runtime probes for observation

Observation should prefer bounded read-only runtime probes over brittle DOM scraping.

### 3. Fail closed on ambiguity

If the MCP cannot prove the APNTalk surface is trustworthy, it must refuse success.

### 4. APNTalk-specific behavior stays in the APNTalk adapter

Do not solve APNTalk fit issues by polluting generic MCP core logic.

### 5. Observation before control

Do not add answer, hangup, or richer call controls until the observation model is stable.

### 6. Runtime truth precedes DOM heuristics

When runtime/store truth and visible DOM disagree, the result is **inconsistent_state**, not success.

### 7. Bounded data exposure only

Store snapshots, peer-connection summaries, and diagnostics must be allowlisted, versioned, and redacted.

### 8. Capability reporting must be truthful at two levels

The tool must distinguish between:

- what the adapter knows how to support, and
- what the current APNTalk session actually exposes.

---

## Canonical Contract Requirement

## Contract 0 — APNTalk Runtime Bridge Contract

Before broad observation support is claimed, APNTalk should expose a versioned read-only browser contract, for example:

- `window.__apnTalkTestBridge`

This must be treated as a formal contract, not a temporary convenience.

### Required Contract Properties

- explicit version field, e.g. `bridgeVersion`
- explicit APNTalk build/app metadata where safe
- read-only getters or immutable snapshots only
- no credential-bearing fields
- no mutating helpers
- stable field names
- timestamps/freshness indicators
- absence must be handled explicitly
- partial availability must be distinguishable from full availability

### Suggested High-Level Shape

```ts
type ApnTalkTestBridgeV1 = {
  bridgeVersion: "1";
  availableAt: string;
  auth: {
    isAuthenticated: boolean | null;
  };
  agent: {
    agentId?: string | null;
    uiLoaded: boolean | null;
    readyState: "unknown" | "not_ready" | "ready" | "busy" | "wrapup" | "offline";
  };
  sip: {
    registrationState:
      | "unknown"
      | "unregistered"
      | "registering"
      | "registered"
      | "failed";
    lastErrorCode?: string | null;
  };
  call: {
    callState:
      | "idle"
      | "incoming"
      | "answering"
      | "active"
      | "held"
      | "ending"
      | "ended"
      | "unknown";
    direction?: "inbound" | "outbound" | "unknown";
    hasVisibleAnswerControl?: boolean | null;
    hasVisibleHangupControl?: boolean | null;
  };
  webrtc: {
    peerConnectionAvailable: boolean | null;
    signalingState?: string | null;
    iceConnectionState?: string | null;
    connectionState?: string | null;
    hasLocalDescription?: boolean | null;
    hasRemoteDescription?: boolean | null;
  };
  diagnostics: {
    websocketReachabilityHint?: "unknown" | "reachable" | "unreachable";
    microphonePermission?: "unknown" | "granted" | "denied" | "prompt";
    autoplayRisk?: "unknown" | "low" | "elevated";
  };
};
```

### Contract Governance Requirements

- versioned contract doc under `telecom-browser-mcp`
- matching APNTalk-side contract implementation notes
- contract tests on the MCP side
- fail-closed behavior when the contract is absent, stale, malformed, or partially incompatible

---

## Canonical State Model

The plan should avoid ambiguous “ready” semantics.

### Authentication State

- `unauthenticated`
- `authenticating`
- `authenticated`
- `auth_failed`
- `unknown`

### UI State

- `ui_not_loaded`
- `ui_loaded`
- `unknown`

### SIP Registration State

- `unregistered`
- `registering`
- `registered`
- `failed`
- `unknown`

### Agent Availability State

- `offline`
- `not_ready`
- `ready`
- `busy`
- `wrapup`
- `unknown`

### Call State

- `idle`
- `incoming`
- `answering`
- `active`
- `held`
- `ending`
- `ended`
- `unknown`

### Derived Readiness Rule

`wait_for_ready` must not mean “the page is open.”

A truthful APNTalk-ready outcome should be explicitly defined. Recommended default:

- authenticated,
- UI loaded,
- SIP registered,
- agent availability state is `ready`,
- no contradictory call/control state.

If APNTalk product semantics require a narrower or broader definition, that definition must be documented and tested.

---

## Capability Truth Model

The plan should distinguish **declared support** from **live detected support**.

### Proposed Capability Fields

```json
{
  "capability": "wait_for_ready",
  "declared_support": "supported_with_runtime_probe",
  "binding_status": "runtime_probe_bound",
  "live_detection_status": "bridge_present",
  "why_unavailable": null
}
```

### Recommended Enumerations

#### declared_support

- `supported`
- `supported_with_runtime_probe`
- `supported_with_selector_binding`
- `blocked_by_product_surface`
- `unsupported_by_design`
- `scaffold_only`

#### binding_status

- `runtime_probe_bound`
- `selector_bound`
- `partially_bound`
- `unbound`

#### live_detection_status

- `detected`
- `bridge_present`
- `bridge_absent`
- `selector_present`
- `selector_absent`
- `inconsistent_state`
- `not_checked`

This prevents a misleading “supported” label when the current session lacks the required APNTalk surface.

---

## Precedence and Inconsistency Rule

When multiple truth surfaces exist, use this precedence order:

1. versioned APNTalk runtime bridge
2. safe browser runtime inspection rooted in known APNTalk/SIP.js structures
3. visible DOM/accessibility confirmation
4. generic fallback heuristics

If higher-priority truth disagrees with lower-priority truth:

- do not guess,
- return `inconsistent_state`,
- include both observations in diagnostics.

Example:
- runtime says `incoming`,
- DOM has no visible answer control.

This is **not success** and **not absence of call**. It is an inconsistency that should be surfaced.

---

## Data Exposure and Redaction Rules

`get_store_snapshot` should not dump arbitrary application stores.

Instead, it should return a normalized, allowlisted, redacted summary.

### Allowed Snapshot Categories

- auth high-level state only
- agent readiness state
- SIP registration state
- current call state
- presence of answer/hangup controls
- peer-connection presence and safe summary fields
- bounded APNTalk adapter notes

### Prohibited Snapshot Data

- tokens
- cookies
- SIP usernames/passwords or auth secrets
- customer PII unless explicitly justified and separately governed
- arbitrary raw store trees
- browser local storage dumps by default

### Snapshot Requirements

- schema version
- redaction marker where needed
- bounded size
- timestamps
- explicit `data_unavailable` markers

---

## Revised Delivery Plan

## Phase 0 — Pilot Baseline, Truthful Capabilities, and Early Diagnostics

### Goal

Make the APNTalk login-only pilot reliable, diagnosable, and explicit about what is and is not supported.

### Work Items

1. Add APNTalk pilot setup documentation.
2. Document URL policy, private/VPN host expectations, browser launch prerequisites, and media permission expectations.
3. Add an `apntalk_login_smoke` scenario.
4. Improve URL-policy and launch-failure error classification.
5. Introduce richer capability truth reporting now, not later.
6. Add minimal session diagnostics:
   - adapter id in use,
   - capability declarations,
   - selector match/miss notes,
   - runtime bridge present/absent,
   - microphone permission state where safe.

### Deliverables

- `docs/apntalk/apntalk-pilot-setup.md`
- `docs/apntalk/apntalk-login-smoke.md`
- updated README/setup guidance
- capability truth reporting baseline
- early APNTalk session diagnostics

### Success Criteria

- a new operator can run a login-only smoke without reverse-engineering the runtime,
- unsupported APNTalk journeys are explained truthfully,
- launch and URL failures are classified clearly.

---

## Phase 1 — Define and Bind the APNTalk Runtime Bridge Contract

### Goal

Create the smallest stable APNTalk read-only observation surface needed for truthful MCP support.

### Work Items

1. Define the versioned APNTalk runtime bridge contract.
2. Add APNTalk adapter support for bridge-aware probing.
3. Add contract tests for:
   - bridge absent,
   - bridge malformed,
   - bridge partial,
   - bridge version mismatch,
   - bridge valid.
4. Ensure all bridge access remains read-only.
5. Add timestamps/freshness validation where relevant.

### Deliverables

- APNTalk bridge contract doc
- updated APNTalk adapter contract
- APNTalk bridge probe implementation
- tests for compatible/incompatible bridge behavior

### Success Criteria

- the MCP can tell whether APNTalk exposes a trustworthy bridge,
- malformed or absent bridges fail closed,
- contract drift becomes test-visible.

---

## Phase 2 — Readiness, Registration, and Safe Snapshot Support

### Goal

Implement the highest-value read-only APNTalk observation surfaces with precise semantics.

### Priority Surfaces

1. `wait_for_ready`
2. `get_registration_status`
3. `get_store_snapshot` (bounded/redacted)
4. `get_active_session_snapshot` improvements

### Work Items

1. Implement readiness using the canonical state model.
2. Implement structured registration status output.
3. Implement redacted allowlisted store/session snapshot output.
4. Add explicit `unknown`, `partial`, and `inconsistent_state` handling.
5. Add tests for success, failure, ambiguous, and missing-surface paths.

### Deliverables

- APNTalk readiness probe support
- APNTalk registration support
- bounded snapshot support
- expanded tests

### Success Criteria

- `wait_for_ready` no longer guesses,
- registration is structured and APNTalk-aware,
- snapshot output is bounded and safe,
- disagreement between surfaces fails closed.

---

## Phase 3 — Early WebRTC Visibility and APNTalk Diagnostics

### Goal

Improve first-pass debugging before incoming-call control work begins.

### Work Items

1. Add APNTalk-aware diagnostics for:
   - login failure,
   - registration failure,
   - bridge absence,
   - inconsistent state,
   - microphone/autoplay issues.
2. Begin peer-connection inspection using the real `sip.js` path:
   - `session.sessionDescriptionHandler.peerConnection`
3. Normalize safe peer-connection fields into MCP summaries.
4. Extend debug bundles with:
   - capability truth metadata,
   - binding status,
   - live detection status,
   - bridge availability,
   - selector match/miss notes,
   - media permission hints,
   - websocket reachability hints where available.

### Deliverables

- richer APNTalk debug bundles
- first meaningful APNTalk `get_peer_connection_summary`
- improved active session snapshot notes

### Success Criteria

- common APNTalk browser failures can be classified on first pass,
- WebRTC evidence is useful before answer/hangup is attempted.

---

## Phase 4 — Incoming-Call Observation

### Goal

Support truthful ring-state detection before enabling more control actions.

### Work Items

1. Implement `wait_for_incoming_call` using bridge/runtime truth first.
2. Use DOM only as secondary confirmation.
3. Return `inconsistent_state` when ring-state truth and visible controls disagree.
4. Add tests for ring transition, timeout, ambiguous state, and absent bridge cases.

### Deliverables

- incoming-call observation support
- ring-state tests
- diagnostic coverage for inconsistent incoming-call surfaces

### Success Criteria

- the MCP can determine that APNTalk is ringing without brittle text scraping,
- ambiguous ring states do not produce false positives.

---

## Phase 5 — Bounded Answer and Hangup

### Goal

Enable the smallest safe control actions only after observation is trustworthy.

### Preconditions

Do not begin Phase 5 until:

- login pilot is stable,
- bridge contract is stable,
- readiness and registration support are stable,
- incoming-call observation is stable,
- answer/hangup controls are visible and consistently detectable.

### Work Items

1. Bind `answer_call` to real visible APNTalk controls.
2. Bind `hangup_call` to real visible APNTalk controls.
3. Require pre-action state confirmation.
4. Require post-action transition confirmation.
5. Refuse action on ambiguous or inconsistent state.
6. Add tests for:
   - valid answer,
   - valid hangup,
   - missing control,
   - no state transition,
   - inconsistent state.

### Deliverables

- bounded APNTalk answer/hangup support
- control-path safety tests

### Success Criteria

- answer/hangup work only when runtime truth and visible UI agree,
- no ambiguous action path reports success.

---

## Phase 6 — Scenario Packs for APNTalk Modernization

### Goal

Turn the MCP from an ad hoc helper into a repeatable modernization companion.

### Scenario Packs

1. APNTalk login smoke
2. APNTalk readiness/registration smoke
3. APNTalk incoming-call observe-only check
4. APNTalk answer/hangup bounded verification
5. APNTalk debug-bundle collection walkthrough
6. APNTalk browser-side SIP/WebRTC troubleshooting walkthrough

### Work Items

1. Add scenario docs and examples.
2. Map each scenario to actual support status.
3. Add bounded operator checklists.
4. Add Codex/agent-oriented usage guidance where useful.

### Deliverables

- scenario docs under `docs/apntalk/`
- example workflows
- operator guidance

### Success Criteria

- APNTalk investigations can reuse the same bounded workflows consistently.

---

## Phase 7 — Later Expansion Wave

### Goal

Consider richer in-call controls only after the bounded pilot proves stable.

### Explicitly Deferred

- DTMF
- mute
- hold
- volume
- conference control
- outbound dial orchestration

### Gate for Reconsideration

Do not schedule these until:

- Phases 0–6 are stable,
- the bridge contract is mature,
- current control paths are truthful,
- APNTalk product surfaces justify the expansion.

---

## Testing and Verification Requirements

Every phase should include:

1. unit tests for absent, partial, malformed, and successful APNTalk surfaces,
2. adapter-contract tests ensuring support is not advertised without a real binding,
3. fail-closed tests for ambiguity and inconsistency,
4. scenario-level smoke coverage where practical,
5. diagnostic bundle assertions for meaningful first-pass debugging.

Recommended minimum negative cases:

- bridge absent
- bridge version mismatch
- bridge malformed
- registration unknown
- readiness ambiguous
- runtime says incoming but answer control absent
- answer control visible but runtime says idle
- peer connection path unavailable
- microphone permission denied
- autoplay/media blocked

---

## Risks and Residual Unknowns

1. APNTalk may not yet expose enough stable frontend/runtime truth to support all desired journeys.
2. The bridge contract may require frontend changes in APNTalk to become stable enough.
3. Browser/media behavior may still vary across private/VPN environments.
4. SIP.js runtime structures may vary by APNTalk version and need careful normalization.
5. Some controls may remain blocked by product surface rather than MCP adapter work.
6. Browser-edge truth will still not replace backend/provider authority.

---

## Best Immediate Next Step

The best next step is to begin with a bounded, contract-first pilot:

1. complete Phase 0 pilot baseline and truthful capability reporting,
2. define Contract 0 for the APNTalk runtime bridge,
3. implement Phase 2 readiness/registration/snapshot support only on top of that contract,
4. add diagnostics and peer-connection visibility before call control,
5. add incoming-call truth and only then answer/hangup.

Do **not** start with DTMF, mute, hold, conference, or broader control surfaces.

---

## Planning Note for Codex or Claude

Preferred execution posture:

- plan first,
- implement in bounded phases,
- verify after every phase,
- keep APNTalk-specific logic inside the APNTalk adapter,
- treat the runtime bridge as a versioned contract,
- fail closed on ambiguity,
- do not broaden scope until the previous phase is stable and evidenced.
