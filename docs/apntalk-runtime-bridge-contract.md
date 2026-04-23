# APNTalk Runtime Bridge Contract

This document defines the consumer-side contract that `telecom-browser-mcp`
validates and consumes from `window.__apnTalkTestBridge`.

This repository does **not** make APNTalk emit the bridge. It only defines the
bounded read-only shape that the APNTalk adapter can inspect when the bridge is
present in a live browser session.

## Purpose

- provide a narrow versioned observation contract
- make bridge drift test-visible
- fail closed when the bridge is absent, malformed, partial, or on an
  unsupported version

The bridge is observation-only. A valid bridge does **not** by itself promote
APNTalk answer, mute, hold, DTMF, or store snapshot support to "working".

## Current Contract

Bridge name:

`window.__apnTalkTestBridge`

Required top-level fields:

- `version`: string, currently `"1.4.0"`
- `readOnly`: boolean, currently `true`
- `mode`: string, currently `"observation-only"`
- `sessionAuth`: object
- `agent`: object
- `registration`: object
- `call`: object
- `readiness`: object
- `incomingCall`: object
- `webRTC`: object
- `peerConnection`: object
- `controls`: object containing `answer` and `hangup`

Required field on each section:

- `availability`: `"available" | "partial" | "unavailable"`

Optional bounded fields:

- `sessionAuth.isAuthenticated`: boolean
- `sessionAuth.hasUser`: boolean
- `sessionAuth.hasSelectedCampaign`: boolean
- `sessionAuth.hasCampaigns`: boolean
- `agent.lifecycleStatus`: non-empty string
- `agent.sessionInitialized`: boolean
- `agent.hasUserId`: boolean
- `agent.hasSessionId`: boolean
- `agent.hasExtension`: boolean
- `registration.isRegistered`: boolean
- `registration.callStatus`: non-empty string
- `registration.hasRegisterer`: boolean
- `registration.hasSession`: boolean
- `registration.hasCallerInfo`: boolean
- `call.hasActiveCall`: boolean
- `call.callStatus`: non-empty string
- `call.direction`: `"incoming" | "inbound" | "outbound" | "unknown"`
- `call.isMuted`: boolean
- `call.isOnHold`: boolean
- `call.durationSeconds`: number or `null`
- `call.hasBridgeId`: boolean
- `readiness.isAuthenticated`: boolean
- `readiness.sessionInitialized`: boolean
- `readiness.lifecycleStatus`: non-empty string
- `readiness.isRegistered`: boolean
- `readiness.requestedAvailability`: non-empty string
- `readiness.effectiveAvailability`: non-empty string
- `incomingCall.isIncomingPresent`: boolean
- `incomingCall.ringingState`: `"idle" | "ringing" | "unknown"`
- `incomingCall.direction`: `"incoming" | "inbound" | "outbound" | "unknown"`
- `incomingCall.ambiguity`: `"none" | "ringing_without_inbound_direction"`
- `webRTC.hasRemoteAudioElement`: boolean
- `webRTC.remoteAudioAttached`: boolean
- `webRTC.hasRingtoneElement`: boolean
- `peerConnection.hasPeerConnection`: boolean
- `peerConnection.ambiguity`: `"none" | "no_active_session" | "session_without_description_handler" | "description_handler_without_peer_connection" | "peer_connection_counts_unavailable"`
- `peerConnection.signalingState`: non-empty string
- `peerConnection.iceConnectionState`: non-empty string
- `peerConnection.connectionState`: non-empty string
- `peerConnection.hasLocalDescription`: boolean
- `peerConnection.hasRemoteDescription`: boolean
- `peerConnection.senderCount`: integer or `null`
- `peerConnection.receiverCount`: integer or `null`
- `peerConnection.transceiverCount`: integer or `null`
- `controls.answer.availability`: `"available" | "partial" | "unavailable"`
- `controls.answer.visible`: boolean
- `controls.answer.enabled`: boolean
- `controls.answer.actionAllowed`: boolean
- `controls.answer.ambiguity`: `"none" | "multiple_main_answer_controls" | "multiple_answer_contexts" | "main_answer_control_unavailable"`
- `controls.answer.controlKind`: non-empty string
- `controls.answer.controlScope`: non-empty string
- `controls.answer.stableControlId`: non-empty string
- `controls.answer.selectorContract`: non-empty string
- `controls.hangup.availability`: `"available" | "partial" | "unavailable"`
- `controls.hangup.visible`: boolean
- `controls.hangup.enabled`: boolean
- `controls.hangup.actionAllowed`: boolean
- `controls.hangup.ambiguity`: `"none" | "multiple_main_hangup_controls" | "multiple_hangup_contexts" | "main_hangup_control_unavailable"`
- `controls.hangup.controlKind`: non-empty string
- `controls.hangup.controlScope`: non-empty string
- `controls.hangup.stableControlId`: non-empty string
- `controls.hangup.selectorContract`: non-empty string

Anything outside this allowlist is ignored by the consumer and must not be
treated as part of the contract.

## Consumer Verdicts

The APNTalk adapter classifies the bridge as exactly one of:

- `bridge_absent`
- `bridge_malformed`
- `bridge_partial`
- `bridge_version_mismatch`
- `bridge_valid`

Interpretation:

- `bridge_absent`: no bridge is exposed on `window`
- `bridge_malformed`: the bridge exists but violates required types or bounded values
- `bridge_partial`: the bridge has the correct top-level metadata but is missing required sections or fields
- `bridge_version_mismatch`: the bridge exposes a different version than the consumer supports
- `bridge_valid`: the bridge satisfies the current consumer contract

## Current Safe Consumer Promotions

The current bounded APNTalk consumer can truthfully use a valid bridge for:

- `get_registration_status`
- `wait_for_registration`, only when bridge-backed registration facts satisfy
  the exact consumer registration contract
- `wait_for_ready`, only when bridge-backed readiness facts satisfy the exact
  consumer ready contract
- `wait_for_incoming_call`, only when bridge-backed incoming-call facts safely
  distinguish ringing incoming state without ambiguity
- `get_peer_connection_summary`, only when bridge-backed peer-connection facts
  satisfy the exact consumer summary contract without ambiguity
- `answer_call`, only when the validated bridge exposes a unique visible
  incoming-call answer control, the selector contract resolves to exactly one
  visible element, a safe incoming ringing target is proven, and a connected
  post-click transition is observed within timeout
- `hangup_call`, only when the validated bridge exposes a unique visible
  main-call hangup control, the selector contract resolves to exactly one
  visible element, an active call target is proven, and a terminal post-click
  transition is observed within timeout

It does **not** use bridge presence alone as success.

It still does **not** promote:

- `get_store_snapshot`
## Safe Surfaces

Validated bridge verdicts and bounded APNTalk observation state can appear in:

- `capabilities`
- `open_app`
- `get_active_session_snapshot`
- `get_registration_status`
- `wait_for_registration`
- `wait_for_ready`
- `wait_for_incoming_call`
- `get_peer_connection_summary`
- `answer_call`
- `hangup_call`

These surfaces report bounded diagnostics and observation results only. They do
not expose arbitrary APNTalk runtime objects or raw sensitive dumps.
