# Telecom Browser MCP

## Revised MCP Server Spec + Python SDK Implementation Plan

Version: v0.2  
Date: 2026-03-07  
Target SDK: `modelcontextprotocol/python-sdk`

---

## 1. Purpose

`telecom-browser-mcp` is a telecom-aware MCP server that gives AI agents a structured, standardized way to automate, inspect, and diagnose WebRTC dialer applications through browser control and runtime inspection.

It is designed to complement `telecom-mcp`, not replace it.

### Role in the stack

`telecom-browser-mcp` owns browser-side truth:

- browser automation
- frontend state inspection
- SIP/WebRTC runtime inspection inside the browser
- browser-side evidence capture
- frontend-focused diagnostics

`telecom-mcp` owns PBX-side truth:

- ARI / AMI / PBX inspection
- backend orchestration validation
- server-side signaling and channel state
- telephony infrastructure diagnostics

### Primary goal

Turn generic browser automation into telecom-aware MCP tools such as:

- `open_app`
- `login_agent`
- `wait_for_registration`
- `wait_for_incoming_call`
- `answer_call`
- `hangup_call`
- `get_active_session_snapshot`
- `get_peer_connection_summary`
- `diagnose_answer_failure`
- `collect_debug_bundle`

---

## 2. Why use the MCP Python SDK

The official MCP Python SDK is the correct foundation because it is the maintained Python implementation for MCP and supports the standard MCP server model, including tools, resources, prompts, and standard transports such as stdio, SSE, and Streamable HTTP. ([github.com](https://github.com/modelcontextprotocol/python-sdk?utm_source=chatgpt.com))

That means this project can align with the protocol instead of inventing a custom JSON-RPC layer, and it improves interoperability with MCP-capable hosts and inspectors. The MCP Inspector itself is designed to test and debug MCP servers across stdio, SSE, and streamable-http transports, which makes it directly useful during development of this server. ([github.com](https://github.com/modelcontextprotocol/python-sdk?utm_source=chatgpt.com))

### Design decision

For `telecom-browser-mcp` v1:

- **required**: tools
- **optional**: a small resource set
- **deferred**: prompts unless a clear host workflow requires them

This keeps the first release focused on the most consistently useful MCP capability: tool execution.

---

## 3. Position in the stack

```text
AI Agent / Codex / Cursor / Claude / other MCP client
                    |
                    v
          telecom-browser-mcp
          ├─ MCP Python SDK server
          ├─ Playwright browser driver
          ├─ adapter registry
          ├─ frontend/runtime inspectors
          ├─ diagnostics engine
          ├─ evidence writer
          └─ session manager
                    |
                    v
              Dialer Web App
                    |
      ┌─────────────┴─────────────┐
      v                           v
 SIP.js / JsSIP runtime      UI store (Vue/Pinia/etc.)
      |
      v
 RTCPeerConnection
```

Optional external integrations:

```text
telecom-browser-mcp
  ├─ telecom-mcp
  ├─ Redis/debug endpoints
  ├─ app observability endpoints
  └─ test harness / fake dialer
```

---

## 4. Design principles

### 4.1 Expose telecom intent, not DOM trivia

Prefer:

- `answer_call()`
- `assert_registered()`
- `get_peer_connection_summary()`

Instead of:

- `click("#answer")`
- `get_text(".badge")`

### 4.2 Contract-first tools

Every tool must have:

- strict input schema
- strict output schema
- declared error codes
- declared artifact behavior
- explicit success criteria

### 4.3 Separate action from assertion

Actions mutate state. Assertions verify state. Diagnostics explain failure.

### 4.4 Prefer stable runtime truth over brittle selectors

When possible, inspect:

- app store slices
- SIP runtime objects
- WebRTC runtime state

before trusting only DOM state.

### 4.5 Evidence by default on failure

A failed tool should return structured artifacts automatically when feasible.

### 4.6 Browser-side scope stays narrow

This MCP does **not** own:

- ARI orchestration
- AMI business logic
- PBX provisioning
- SIP load generation
- infrastructure lifecycle control

---

## 5. Scope

### 5.1 v1 scope

- open app
- login agent
- wait for ready
- wait for registration
- detect incoming call
- answer call
- hangup call
- inspect UI/store/runtime/session state
- inspect peer connection summary
- collect debug bundle
- diagnose registration / incoming / answer failures
- close/reset/list browser sessions

### 5.2 v2 scope

- dial outbound
- mute/unmute
- hold/resume
- transfer
- reconnect handling
- multi-call handling
- contract validation mode
- richer one-way-audio diagnostics
- limited resources and prompt templates if proven useful

### 5.3 out of scope for initial release

- RTP packet capture outside the browser
- MOS / full media quality scoring
- PBX cluster control
- arbitrary browser automation outside telecom flows
- arbitrary JavaScript execution exposed to agents

---

## 6. High-level architecture

```text
src/
├─ telecom_browser_mcp/
│  ├─ server/
│  │  ├─ stdio_server.py
│  │  ├─ sse_server.py
│  │  └─ app.py
│  ├─ config/
│  │  ├─ settings.py
│  │  ├─ schemas.py
│  │  └─ allowlists.py
│  ├─ sessions/
│  │  ├─ manager.py
│  │  ├─ browser_session.py
│  │  └─ lifecycle.py
│  ├─ browser/
│  │  ├─ playwright_driver.py
│  │  ├─ context_factory.py
│  │  └─ permissions.py
│  ├─ adapters/
│  │  ├─ base.py
│  │  ├─ registry.py
│  │  ├─ generic_sipjs.py
│  │  └─ generic_jssip.py
│  ├─ inspectors/
│  │  ├─ ui_inspector.py
│  │  ├─ store_inspector.py
│  │  ├─ sip_inspector.py
│  │  ├─ webrtc_inspector.py
│  │  └─ environment_inspector.py
│  ├─ diagnostics/
│  │  ├─ registration.py
│  │  ├─ incoming_call.py
│  │  ├─ answer_flow.py
│  │  ├─ one_way_audio.py
│  │  └─ rules.py
│  ├─ evidence/
│  │  ├─ artifact_paths.py
│  │  ├─ redaction.py
│  │  ├─ screenshot_writer.py
│  │  ├─ bundle_writer.py
│  │  └─ markdown_report.py
│  ├─ models/
│  │  ├─ enums.py
│  │  ├─ session.py
│  │  ├─ registration.py
│  │  ├─ call.py
│  │  ├─ webrtc.py
│  │  ├─ artifact.py
│  │  └─ diagnostic.py
│  ├─ tools/
│  │  ├─ session_tools.py
│  │  ├─ registration_tools.py
│  │  ├─ call_tools.py
│  │  ├─ inspection_tools.py
│  │  ├─ diagnostic_tools.py
│  │  └─ evidence_tools.py
│  └─ resources/
│     └─ session_resources.py
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ e2e/
│  └─ fixtures/
└─ scripts/
```

---

## 7. Transport and runtime choices

The Python SDK supports stdio, SSE, and Streamable HTTP. ([github.com](https://github.com/modelcontextprotocol/python-sdk?utm_source=chatgpt.com))

### v1 transport policy

- local dev default: `stdio`
- hosted/service mode: `SSE`
- Streamable HTTP: optional later if an actual host requires it

### compatibility goal

Validate at least:

- one local stdio host
- one remote/network transport path
- MCP Inspector for manual debugging and protocol verification ([github.com](https://github.com/modelcontextprotocol/inspector?utm_source=chatgpt.com))

### session policy

- v1 default: one active browser session per MCP client session
- multi-session support: explicit and opt-in
- all sessions must be trackable and cleanly closable

---

## 8. Core domain model

## 8.1 BrowserSession

Represents one controlled browser context.

Fields:

- `session_id`
- `run_id`
- `status` (`active`, `closing`, `closed`, `broken`)
- `adapter_name`
- `adapter_version`
- `base_url`
- `origin`
- `headless`
- `browser_type`
- `environment_classification`
- `created_at`
- `last_activity_at`
- `current_page_url`
- `page_title`
- `artifacts_dir`

## 8.2 RegistrationSnapshot

Fields:

- `state` (`unknown`, `initializing`, `connecting`, `registered`, `failed`)
- `ui_badge_state`
- `sip_stack_state`
- `ws_connected`
- `registered`
- `last_error`
- `source_confidence`
- `timestamp`

## 8.3 CallSnapshot

Fields:

- `call_id`
- `direction`
- `state` (`idle`, `ringing`, `answering`, `connected`, `ending`, `ended`, `failed`)
- `ui_state`
- `store_state`
- `sip_session_state`
- `remote_number`
- `local_number`
- `started_at`
- `connected_at`
- `ended_at`
- `is_muted`
- `is_on_hold`
- `correlation_keys`

## 8.4 WebRtcSnapshot

Fields:

- `peer_connection_present`
- `connection_state`
- `ice_connection_state`
- `signaling_state`
- `local_audio_tracks`
- `remote_audio_tracks`
- `candidate_pair_state`
- `inbound_rtp_audio_packets`
- `outbound_rtp_audio_packets`
- `timestamp`

## 8.5 DiagnosticResult

Fields:

- `summary`
- `findings[]`
- `likely_causes[]`
- `severity`
- `failure_category`
- `retryable`
- `artifacts[]`
- `next_recommended_tools[]`
- `timestamp`

## 8.6 ArtifactRef

Fields:

- `type`
- `label`
- `path`
- `redacted`
- `created_at`

---

## 9. State model

The server must normalize major states into enums instead of free-form strings wherever possible.

### Registration states

- `unknown`
- `initializing`
- `connecting`
- `registered`
- `failed`

### Call states

- `idle`
- `ringing`
- `answering`
- `connected`
- `ending`
- `ended`
- `failed`

### Browser session states

- `active`
- `closing`
- `closed`
- `broken`

### WebRTC states

- `missing`
- `new`
- `connecting`
- `connected`
- `failed`
- `closed`

This is required so diagnostics and agents can reason consistently across adapters.

---

## 10. Adapter model

An adapter makes the server app-aware.

Each adapter defines:

- login selectors and flow
- ready-state rules
- registration rules
- incoming call detection rules
- answer/hangup selectors and fallbacks
- store access hooks
- SIP runtime hooks
- normalization logic for snapshots
- explicit compatibility/version notes

### Required adapter interface

```python
class TelecomAdapter(Protocol):
    name: str
    version: str

    async def open_app(self, session, url: str) -> dict: ...
    async def login_agent(self, session, username: str, password: str, tenant: str | None = None) -> dict: ...
    async def wait_for_ready(self, session, timeout_ms: int = 30000) -> dict: ...

    async def get_registration_snapshot(self, session) -> dict: ...
    async def wait_for_registration(self, session, expected: str = "registered", timeout_ms: int = 30000) -> dict: ...

    async def wait_for_incoming_call(self, session, timeout_ms: int = 30000) -> dict: ...
    async def answer_call(self, session, call_ref: str | None = None, timeout_ms: int = 15000) -> dict: ...
    async def hangup_call(self, session, call_ref: str | None = None, timeout_ms: int = 15000) -> dict: ...

    async def get_ui_call_state(self, session) -> dict: ...
    async def get_store_snapshot(self, session) -> dict: ...
    async def get_active_session_snapshot(self, session) -> dict: ...
    async def get_peer_connection_summary(self, session) -> dict: ...
```

### Adapter policy

- adapter outputs must normalize into shared models
- adapter-specific raw data may be attached in debug mode only
- every adapter must ship with smoke tests
- every adapter must declare the selectors/runtime assumptions it relies on

### Initial adapters

- `generic_sipjs`
- `generic_jssip`



---

## 11. MCP tool catalog

## 11.1 Session tools

### `open_app`

Open the dialer app and create a managed browser session.

### `login_agent`

Log into the dialer UI.

### `wait_for_ready`

Wait until bootstrap and required runtime surfaces are ready.

### `list_sessions`

Return all active or recoverable browser sessions.

### `close_session`

Close a specific session cleanly.

### `reset_session`

Reload or rebuild a broken session according to policy.

---

## 11.2 Registration tools

### `get_registration_status`

Return a normalized `RegistrationSnapshot`.

### `wait_for_registration`

Wait until registration matches expected state.

### `assert_registered`

Fail if not registered and attach evidence.

---

## 11.3 Call tools

### `wait_for_incoming_call`

Wait until an incoming call is detected via UI and/or runtime.

### `answer_call`

Attempt to answer a call and verify transition.

### `hangup_call`

End the active call.

### `get_ui_call_state`

Read normalized UI-visible call state.

### `get_active_session_snapshot`

Return normalized SIP/call runtime state.

---

## 11.4 Inspection tools

### `get_store_snapshot`

Return only approved, relevant store slices.

### `get_peer_connection_summary`

Return normalized peer connection state.

### `get_webrtc_stats`

Return normalized browser `getStats()` output for diagnostics.

### `get_environment_snapshot`

Return environment signals that affect media/browser behavior.

---

## 11.5 Diagnostic tools

### `diagnose_registration_failure`

Investigate registration breakdown.

### `diagnose_incoming_call_failure`

Investigate why an expected incoming call was not surfaced or handled.

### `diagnose_answer_failure`

Investigate why answer did not become a connected call.

### `diagnose_one_way_audio`

Defer implementation if needed, but reserve the schema early.

---

## 11.6 Evidence tools

### `screenshot`

Capture redacted screenshot where possible.

### `collect_browser_logs`

Collect sanitized console and selected network summaries.

### `collect_debug_bundle`

Create a structured evidence bundle.

---

## 12. Tool contract rules

Every tool response must include:

- `ok`
- `timestamp`
- `session_id` when applicable
- `duration_ms`
- `artifacts[]`
- `warnings[]`

Every failure response must additionally include:

- `error_code`
- `message`
- `failure_category`
- `retryable`
- `likely_causes[]`
- `next_recommended_tools[]`

### Example failure response

```json
{
  "ok": false,
  "session_id": "sess_123",
  "duration_ms": 12014,
  "error_code": "ANSWER_FLOW_FAILED",
  "failure_category": "call_control",
  "retryable": false,
  "message": "Answer click completed but call did not transition to connected.",
  "likely_causes": [
    "frontend state transition gap",
    "session binding mismatch",
    "backend answer acknowledgment missing"
  ],
  "next_recommended_tools": [
    "get_active_session_snapshot",
    "get_peer_connection_summary",
    "collect_debug_bundle",
    "diagnose_answer_failure"
  ],
  "artifacts": [
    {
      "type": "screenshot",
      "label": "after-answer",
      "path": "docs/audit/telecom-browser-mcp/run-20260307T101422Z/screenshots/002-after-answer.png",
      "redacted": true,
      "created_at": "2026-03-07T10:14:23Z"
    }
  ],
  "warnings": [
    "No RTCPeerConnection found within 10s"
  ],
  "timestamp": "2026-03-07T10:14:24Z"
}
```

---

## 13. Resource catalog

Resources are optional in v1 and should remain minimal.

### Suggested v1 resources

- `session://{session_id}/registration`
- `session://{session_id}/active-call`
- `session://{session_id}/webrtc-summary`

### Deferred resources

- full store snapshots
- raw logs
- artifact browsing trees

The goal is to avoid over-building resources before host behavior proves them useful.

---

## 14. Prompt catalog

Prompt templates are deferred by default.

Possible future prompts:

- `debug-answer-failure`
- `debug-registration-failure`
- `summarize-session-health`

Only add them once a concrete MCP host workflow benefits from them.

---

## 15. Evidence and report layout

Use dynamic run folders and stable filenames inside each run.

```text
docs/
  audit/
    telecom-browser-mcp/
      2026-03-07/
        run-20260307T101422Z/
          summary.json
          report.md
          screenshots/
            001-before-answer.png
            002-after-answer.png
          logs/
            browser-console.json
            network-summary.json
          runtime/
            registration.json
            active-session.json
            webrtc-summary.json
            webrtc-stats.json
            environment.json
```

### Naming rules

- root audit dir: `docs/audit/telecom-browser-mcp`
- run dir: `run-YYYYMMDDTHHMMSSZ`
- stable file names inside each run
- every artifact referenced in tool output must exist on disk if claimed

---

## 16. Security model

The MCP ecosystem includes powerful server capabilities and reference implementations are not automatically production-safe, so this project must narrow permissions aggressively and make trust boundaries explicit. The official reference-servers repository itself warns that example/reference servers are not production-ready and developers must implement their own safeguards. ([github.com](https://github.com/modelcontextprotocol/servers?utm_source=chatgpt.com))

### Security rules

- no arbitrary JavaScript execution tool in v1
- no arbitrary selector click tool in v1
- no unrestricted navigation after session creation
- no filesystem browsing outside configured artifact roots
- no unrestricted browser storage dump by default
- no raw secret echo in tool results
- no unrestricted origin access; require allowlist
- separate debug mode from standard mode

### Redaction rules

- never return passwords
- redact tokens/cookies/auth headers
- redact known secret-bearing log fields
- support screenshot redaction for visible secrets where practical
- avoid returning full network payloads unless sanitized

### Guardrails

- adapter allowlist
- origin allowlist
- per-tool timeout caps
- session isolation
- artifact retention policy
- explicit environment classification for sandbox/CI/media-limit cases

---

## 17. Failure taxonomy

Normalize errors into categories such as:

- `UI_SELECTOR_FAILURE`
- `APP_NOT_READY`
- `REGISTRATION_TIMEOUT`
- `INCOMING_CALL_TIMEOUT`
- `ANSWER_FLOW_FAILED`
- `PEER_CONNECTION_MISSING`
- `WEBRTC_STATE_UNAVAILABLE`
- `ADAPTER_CONTRACT_ERROR`
- `BROWSER_SESSION_BROKEN`
- `ENVIRONMENT_LIMITATION`

These must map to both machine-readable error codes and human-readable explanations.

---

## 18. Observability model

Each tool should emit consistent telemetry:

- start timestamp
- end timestamp
- duration
- session id
- adapter name
- run id
- artifacts created
- warnings
- environment classification if relevant

### Read classification

Inspection responses should distinguish between:

- **stable reads**: URL, title, registration state, runtime object existence, normalized store slice
- **volatile reads**: popup visibility, transient ICE state, one-time stats counters

This helps agents understand whether they are reading durable state or timing-sensitive telemetry.

---

## 19. Correlation model with telecom-mcp

Cross-MCP debugging will be much easier if both systems can align on a shared correlation contract.

### Suggested correlation keys

- `session_id`
- `run_id`
- `agent_id`
- `extension`
- `frontend_call_id`
- `sip_call_id`
- `telecom_mcp_correlation_id`
- normalized timestamps in UTC

This should be defined early, even if the full integration lands later.

---

## 20. Suggested Python package setup

```text
telecom-browser-mcp/
├─ pyproject.toml
├─ README.md
├─ .env.example
├─ src/telecom_browser_mcp/
├─ tests/
├─ docs/
└─ scripts/
```

### Suggested dependencies

- `mcp`
- `playwright`
- `pydantic`
- `tenacity`
- `structlog` or stdlib logging
- `anyio` if useful with runtime integration

Browser binaries should be installed separately as part of setup.

---

## 21. Implementation plan

## Phase 0 — foundation and repo bootstrap

### Goals

- create repo skeleton
- pin Python version
- install MCP SDK and Playwright
- establish lint/test/tooling
- establish strict schemas and shared enums first

### Tasks

1. Initialize repo and `pyproject.toml`
2. Add SDK dependency and Playwright
3. Add format/lint/test tools
4. Add `.env.example`
5. Add initial README and architecture note
6. Add browser install script
7. Define shared response envelope, artifact model, and enums

### Deliverables

- runnable package skeleton
- local bootstrap docs
- hello-world MCP server process
- shared schema module

---

## Phase 1 — minimal MCP server with session lifecycle

### Goals

- start MCP server via Python SDK
- support `open_app`, `login_agent`, `wait_for_ready`
- establish browser session lifecycle
- support `list_sessions`, `close_session`

### Tasks

1. Create server entrypoint
2. Register initial tools
3. Build `BrowserSession` manager
4. Implement Playwright driver wrapper
5. Implement structured tool response envelope
6. Add artifact directory creation per run
7. Add cleanup guarantees for normal and failed exits

### Exit criteria

- agent can start server
- browser session can be created and closed reliably
- login works against a test page or adapter harness

---

## Phase 2 — adapter framework

### Goals

- isolate app-specific logic cleanly
- normalize outputs across UIs

### Tasks

1. Define `TelecomAdapter` interface
2. Build adapter registry
4. Add `generic_sipjs` scaffold
5. Add adapter smoke tests
6. Document adapter assumptions

### Exit criteria

- same tool names work through at least two adapters or one real adapter plus one harness adapter

---

## Phase 3 — registration inspection

### Goals

- inspect registration reliably
- differentiate UI vs runtime truth

### Tasks

1. Build `store_inspector`
2. Build `sip_inspector`
3. Implement `get_registration_status`
4. Implement `wait_for_registration`
5. Implement `assert_registered`
6. Add evidence capture on timeout/failure

### Exit criteria

- system can distinguish:
  - UI says registered / runtime disagrees
  - runtime says registered / UI stale
  - no registration due to environment constraints

---

## Phase 4 — inbound call flow tools

### Goals

- detect incoming call
- answer call
- hangup call
- inspect state transitions

### Tasks

1. Implement `wait_for_incoming_call`
2. Implement `answer_call`
3. Implement `hangup_call`
4. Implement `get_ui_call_state`
5. Implement `get_active_session_snapshot`
6. Add transition waits and retry rules for transient UI issues only

### Exit criteria

- tool flow can capture `ringing -> connected -> ended`
- failures are classified rather than returned as generic timeouts

---

## Phase 5 — evidence and persistent reporting

### Goals

- standardize artifacts early
- make failed runs reusable for debugging

### Tasks

1. Build artifact model and writer
2. Standardize run directory layout
3. Implement `screenshot`
4. Implement `collect_browser_logs`
5. Implement `collect_debug_bundle`
6. Add markdown and JSON summary generation
7. Add redaction pass

### Exit criteria

- every failed action can produce a reusable evidence package

---

## Phase 6 — diagnostics engine

### Goals

- provide useful explanations, not only failure codes

### Tasks

1. Implement `diagnose_registration_failure`
2. Implement `diagnose_incoming_call_failure`
3. Implement `diagnose_answer_failure`
4. Add likely-cause rules
5. Add severity assignment
6. Add next-recommended-tool suggestions

### Exit criteria

- failures return structured reasoning and next steps

---

## Phase 7 — WebRTC inspector

### Goals

- surface peer connection state and browser-side media clues

### Tasks

1. Implement `webrtc_inspector`
2. Add peer connection enumeration
3. Add summary normalization
4. Implement `get_webrtc_stats`
5. Implement `get_peer_connection_summary`
6. Add missing-peer-connection warning paths

### Exit criteria

- after answer, MCP can state whether a peer connection exists and whether RTP counters move

---

## Phase 8 — SSE mode and host compatibility

### Goals

- support broader MCP-host compatibility

### Tasks

1. Add SSE entrypoint
2. Add runtime transport config
3. Validate with at least two MCP hosts
4. Validate with MCP Inspector
5. Document launch examples and payload limits

### Exit criteria

- works with one local stdio host and one remote/service-style host

---

## Phase 9 — integration with telecom-mcp

### Goals

- bridge browser truth with PBX truth

### Tasks

1. Define handoff contract
2. Align correlation fields
3. Add combined evidence report template
4. Build sample end-to-end scenario docs
5. Add example timelines across browser and PBX evidence

### Exit criteria

- a single incident can be correlated across frontend and PBX tooling

---

## Phase 10 — production hardening

### Goals

- make repeated use safe and stable

### Tasks

1. add timeout governance
2. add browser cleanup guarantees
3. add secret redaction hardening
4. add safe logging defaults
5. add stale session cleanup
6. add retry policy for transient UI issues only
7. add environment classification logic
8. add artifact retention policy
9. add launch/health documentation for supported hosts

### Exit criteria

- repeated runs do not leak sessions, artifacts, or secrets
- failures are cleanly classified and recoverable where appropriate

---

## 22. Suggested implementation order for your project



1. `Phase 0`
2. `Phase 1`
4. `Phase 3`
5. `Phase 4`
6. `Phase 5`
7. `Phase 6`
8. `Phase 7`
9. `Phase 8`
10. `Phase 9`
11. `Phase 10`

### Why this order

- you need usable automation early
- your highest-value problem is registration plus inbound-answer debugging
- evidence should arrive before deep diagnostics mature
- diagnostics are more useful once evidence is consistent
- WebRTC inspection is valuable, but not before core call-path observability exists

---

## 23. First milestone recommendation

### Milestone M1 — inbound debug assistant

Include:

- `open_app`
- `login_agent`
- `wait_for_ready`
- `wait_for_registration`
- `wait_for_incoming_call`
- `answer_call`
- `get_active_session_snapshot`
- `get_peer_connection_summary`
- `collect_debug_bundle`
- `diagnose_answer_failure`
- `close_session`
- `list_sessions`

### Why this is the right first milestone

This directly targets the class of issues you have already been dealing with:

- backend originated the call
- frontend received or partly received it
- answer failed or stalled
- state drift exists between backend orchestration and frontend store/runtime

---

## 24. Example tool schema style

Use small, strict schemas.

```python
class WaitForIncomingCallInput(BaseModel):
    session_id: str
    timeout_ms: int = 30000

class ArtifactRef(BaseModel):
    type: str
    label: str
    path: str
    redacted: bool = True
    created_at: str

class WaitForIncomingCallOutput(BaseModel):
    ok: bool
    session_id: str
    call_id: str | None = None
    remote_number: str | None = None
    ui_state: str | None = None
    detected_via: str
    timestamp: str
    duration_ms: int
    artifacts: list[ArtifactRef] = []
    warnings: list[str] = []
```

The same rule should apply to all tools: strict inputs, strict outputs, declared failure shapes.

---

## 25. Testing strategy

### Unit tests

- adapters normalize correctly
- inspectors parse runtime safely
- diagnostics classify known cases correctly
- schemas reject malformed payloads

### Integration tests

- local fake dialer page
- synthetic SIP runtime
- synthetic incoming-call UI state
- fake peer connection snapshots

### End-to-end tests

- real dialer login
- real registration
- real inbound delivery
- real answer/hangup path

### Important addition: fake dialer harness

Create a small test harness page early. It should simulate:

- registration success/failure
- incoming-call popup
- answer success/failure
- peer connection present/missing
- store/runtime divergence

This lets the MCP evolve without depending on a live PBX for every change.

---

## 26. Risks and mitigations

### Risk: app internals change often  
Mitigation: adapter pattern plus normalized models.

### Risk: browser sandbox and media permission issues  
Mitigation: classify environment failures explicitly and capture environment evidence.

### Risk: selectors drift  
Mitigation: prefer runtime/store inspection over selector-only logic.

### Risk: logs and screenshots leak secrets  
Mitigation: redaction pipeline and strict artifact policy.

### Risk: v1 grows too large  
Mitigation: keep v1 focused on inbound/answer diagnostics and session hygiene.

### Risk: different MCP hosts behave differently  
Mitigation: test stdio and SSE explicitly, and use MCP Inspector during development. ([github.com](https://github.com/modelcontextprotocol/inspector?utm_source=chatgpt.com))

---

## 27. Final recommendation

Build `telecom-browser-mcp` as a **browser-side telecom observability and control layer**, not as a general browser automation server.

The MCP Python SDK is the right base because it supports the MCP capability model and standard transports, which helps keep the project protocol-aligned and interoperable. ([github.com](https://github.com/modelcontextprotocol/python-sdk?utm_source=chatgpt.com))

The most valuable first payoff is not “full automation.”

It is this:

**When a call reaches the frontend but the answer flow fails, the MCP should explain why, classify the failure, and produce reusable evidence.**

That is the first meaningful milestone.
