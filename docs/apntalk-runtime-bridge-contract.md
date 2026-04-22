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
APNTalk answer, hangup, mute, hold, DTMF, store snapshot, or peer-connection
summary support to "working".

## Current Contract

Bridge name:

`window.__apnTalkTestBridge`

Required top-level fields:

- `version`: string, currently `"1.1.0"`
- `readOnly`: boolean, currently `true`
- `mode`: string, currently `"observation-only"`
- `sessionAuth`: object
- `agent`: object
- `registration`: object
- `call`: object
- `readiness`: object
- `incomingCall`: object
- `webRTC`: object

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
- `wait_for_ready`, only when bridge-backed readiness facts satisfy the exact
  consumer ready contract
- `wait_for_incoming_call`, only when bridge-backed incoming-call facts safely
  distinguish ringing incoming state without ambiguity

It does **not** use bridge presence alone as success.

It still does **not** promote:

- `wait_for_registration`
- `answer_call`
- `hangup_call`
- `get_store_snapshot`
- `get_peer_connection_summary`

## Safe Surfaces

Validated bridge verdicts and bounded APNTalk observation state can appear in:

- `capabilities`
- `open_app`
- `get_active_session_snapshot`
- `get_registration_status`
- `wait_for_ready`
- `wait_for_incoming_call`

These surfaces report bounded diagnostics and observation results only. They do
not expose arbitrary APNTalk runtime objects or raw sensitive dumps.
