from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class APNTalkSurfaceContract:
    tool_name: str
    selector_name: str | None = None
    selector_css: str | None = None
    runtime_probe_name: str | None = None
    runtime_probe_path: str | None = None

    @property
    def is_implemented(self) -> bool:
        if self.selector_name and not self.selector_css:
            return False
        if self.runtime_probe_name and not self.runtime_probe_path:
            return False
        return True

    def missing_requirements(self) -> list[str]:
        missing: list[str] = []
        if self.selector_name and not self.selector_css:
            missing.append(f"selector:{self.selector_name}")
        if self.runtime_probe_name and not self.runtime_probe_path:
            missing.append(f"runtime_probe:{self.runtime_probe_name}")
        return missing


APNTALK_CONTRACT_VERSION = "apntalk.v1"
APNTALK_RUNTIME_BRIDGE_NAME = "__apnTalkTestBridge"
APNTALK_RUNTIME_BRIDGE_VERSION = "1.4.0"
APNTALK_RUNTIME_BRIDGE_MODE = "observation-only"
APNTALK_RUNTIME_BRIDGE_REQUIRED_SECTIONS = (
    "sessionAuth",
    "agent",
    "registration",
    "call",
    "readiness",
    "incomingCall",
    "webRTC",
    "peerConnection",
    "controls",
)

_SECTION_AVAILABILITY_VALUES = {"available", "partial", "unavailable"}
_CALL_DIRECTION_VALUES = {"incoming", "inbound", "outbound", "unknown"}
_INCOMING_RINGING_STATE_VALUES = {"idle", "ringing", "unknown"}
_INCOMING_AMBIGUITY_VALUES = {"none", "ringing_without_inbound_direction"}
_PEER_CONNECTION_AMBIGUITY_VALUES = {
    "none",
    "no_active_session",
    "session_without_description_handler",
    "description_handler_without_peer_connection",
    "peer_connection_counts_unavailable",
}
_CONTROL_AVAILABILITY_VALUES = {"available", "partial", "unavailable"}
_ANSWER_CONTROL_AMBIGUITY_VALUES = {
    "none",
    "multiple_main_answer_controls",
    "multiple_answer_contexts",
    "main_answer_control_unavailable",
}
_HANGUP_CONTROL_AMBIGUITY_VALUES = {
    "none",
    "multiple_main_hangup_controls",
    "multiple_hangup_contexts",
    "main_hangup_control_unavailable",
}


@dataclass(frozen=True)
class APNTalkRuntimeBridgeContract:
    bridge_name: str = APNTALK_RUNTIME_BRIDGE_NAME
    version: str = APNTALK_RUNTIME_BRIDGE_VERSION
    read_only: bool = True
    mode: str = APNTALK_RUNTIME_BRIDGE_MODE
    required_sections: tuple[str, ...] = APNTALK_RUNTIME_BRIDGE_REQUIRED_SECTIONS


@dataclass(frozen=True)
class APNTalkBridgeValidationResult:
    verdict: str
    bridge_name: str
    bridge_version: str | None = None
    read_only: bool | None = None
    mode: str | None = None
    sections_present: tuple[str, ...] = ()
    sections_missing: tuple[str, ...] = ()
    malformed_fields: tuple[str, ...] = ()
    why_unavailable: str | None = None


APNTALK_RUNTIME_BRIDGE_CONTRACT = APNTalkRuntimeBridgeContract()


def _string_field(payload: dict[str, Any], field_name: str) -> str | None:
    value = payload.get(field_name)
    if isinstance(value, str) and value.strip():
        return value
    return None


def _optional_bool(payload: dict[str, Any], field_name: str, malformed_fields: list[str]) -> None:
    value = payload.get(field_name)
    if value is None or isinstance(value, bool):
        return
    malformed_fields.append(field_name)


def _optional_nonempty_string(
    payload: dict[str, Any],
    field_name: str,
    malformed_fields: list[str],
) -> None:
    value = payload.get(field_name)
    if value is None:
        return
    if isinstance(value, str) and value.strip():
        return
    malformed_fields.append(field_name)


def _optional_enum(
    payload: dict[str, Any],
    field_name: str,
    allowed: set[str],
    malformed_fields: list[str],
) -> None:
    value = payload.get(field_name)
    if value is None:
        return
    if isinstance(value, str) and value in allowed:
        return
    malformed_fields.append(field_name)


def validate_apntalk_runtime_bridge(payload: Any) -> APNTalkBridgeValidationResult:
    contract = APNTALK_RUNTIME_BRIDGE_CONTRACT
    if payload is None:
        return APNTalkBridgeValidationResult(
            verdict="bridge_absent",
            bridge_name=contract.bridge_name,
            why_unavailable=f"{contract.bridge_name} is not present on window",
        )
    if not isinstance(payload, dict):
        return APNTalkBridgeValidationResult(
            verdict="bridge_malformed",
            bridge_name=contract.bridge_name,
            why_unavailable="bridge payload is not an object",
        )

    bridge_version = payload.get("version")
    if isinstance(bridge_version, str) and bridge_version != contract.version:
        return APNTalkBridgeValidationResult(
            verdict="bridge_version_mismatch",
            bridge_name=contract.bridge_name,
            bridge_version=bridge_version,
            read_only=payload.get("readOnly") if isinstance(payload.get("readOnly"), bool) else None,
            mode=_string_field(payload, "mode"),
            why_unavailable=(
                f"bridge version={bridge_version} does not match "
                f"consumer-supported version {contract.version}"
            ),
        )

    malformed_fields: list[str] = []
    if not isinstance(bridge_version, str) or not bridge_version.strip():
        malformed_fields.append("version")

    read_only = payload.get("readOnly")
    if read_only is not True:
        malformed_fields.append("readOnly")

    mode = payload.get("mode")
    if mode != contract.mode:
        malformed_fields.append("mode")

    sections_present: list[str] = []
    sections_missing: list[str] = []
    for section_name in contract.required_sections:
        section = payload.get(section_name)
        if section is None:
            sections_missing.append(section_name)
            continue
        if not isinstance(section, dict):
            malformed_fields.append(section_name)
            continue
        if section_name == "controls":
            answer = section.get("answer")
            if answer is None:
                sections_missing.append("controls.answer")
            elif not isinstance(answer, dict):
                malformed_fields.append("controls.answer")
            else:
                answer_availability = answer.get("availability")
                if answer_availability is None:
                    sections_missing.append("controls.answer.availability")
                elif (
                    not isinstance(answer_availability, str)
                    or answer_availability not in _CONTROL_AVAILABILITY_VALUES
                ):
                    malformed_fields.append("controls.answer.availability")
                for field_name in ("visible", "enabled", "actionAllowed"):
                    _optional_bool(answer, field_name, malformed_fields)
                _optional_enum(answer, "ambiguity", _ANSWER_CONTROL_AMBIGUITY_VALUES, malformed_fields)
                for field_name in ("controlKind", "controlScope", "stableControlId", "selectorContract"):
                    _optional_nonempty_string(answer, field_name, malformed_fields)

            hangup = section.get("hangup")
            if hangup is None:
                sections_missing.append("controls.hangup")
                continue
            if not isinstance(hangup, dict):
                malformed_fields.append("controls.hangup")
                continue
            availability = hangup.get("availability")
            if availability is None:
                sections_missing.append("controls.hangup.availability")
            elif not isinstance(availability, str) or availability not in _CONTROL_AVAILABILITY_VALUES:
                malformed_fields.append("controls.hangup.availability")
            if (
                isinstance(answer, dict)
                and isinstance(answer.get("availability"), str)
                and answer.get("availability") in _CONTROL_AVAILABILITY_VALUES
                and isinstance(hangup, dict)
                and isinstance(hangup.get("availability"), str)
                and hangup.get("availability") in _CONTROL_AVAILABILITY_VALUES
            ):
                sections_present.append(section_name)

            for field_name in ("visible", "enabled", "actionAllowed"):
                _optional_bool(hangup, field_name, malformed_fields)
            _optional_enum(hangup, "ambiguity", _HANGUP_CONTROL_AMBIGUITY_VALUES, malformed_fields)
            for field_name in ("controlKind", "controlScope", "stableControlId", "selectorContract"):
                _optional_nonempty_string(hangup, field_name, malformed_fields)
            continue
        availability = section.get("availability")
        if availability is None:
            sections_missing.append(f"{section_name}.availability")
        elif not isinstance(availability, str) or availability not in _SECTION_AVAILABILITY_VALUES:
            malformed_fields.append(f"{section_name}.availability")
        else:
            sections_present.append(section_name)

        if section_name == "sessionAuth":
            for field_name in ("isAuthenticated", "hasUser", "hasSelectedCampaign", "hasCampaigns"):
                _optional_bool(section, field_name, malformed_fields)
        elif section_name == "agent":
            _optional_nonempty_string(section, "lifecycleStatus", malformed_fields)
            for field_name in ("sessionInitialized", "hasUserId", "hasSessionId", "hasExtension"):
                _optional_bool(section, field_name, malformed_fields)
        elif section_name == "registration":
            _optional_bool(section, "isRegistered", malformed_fields)
            _optional_nonempty_string(section, "callStatus", malformed_fields)
            for field_name in ("hasRegisterer", "hasSession", "hasCallerInfo"):
                _optional_bool(section, field_name, malformed_fields)
        elif section_name == "call":
            _optional_bool(section, "hasActiveCall", malformed_fields)
            _optional_nonempty_string(section, "callStatus", malformed_fields)
            _optional_enum(section, "direction", _CALL_DIRECTION_VALUES, malformed_fields)
            for field_name in ("isMuted", "isOnHold", "hasBridgeId"):
                _optional_bool(section, field_name, malformed_fields)
            duration_seconds = section.get("durationSeconds")
            if duration_seconds is not None and not isinstance(duration_seconds, (int, float)):
                malformed_fields.append("call.durationSeconds")
        elif section_name == "readiness":
            _optional_bool(section, "isAuthenticated", malformed_fields)
            _optional_bool(section, "sessionInitialized", malformed_fields)
            _optional_nonempty_string(section, "lifecycleStatus", malformed_fields)
            _optional_bool(section, "isRegistered", malformed_fields)
            _optional_nonempty_string(section, "requestedAvailability", malformed_fields)
            _optional_nonempty_string(section, "effectiveAvailability", malformed_fields)
        elif section_name == "incomingCall":
            _optional_bool(section, "isIncomingPresent", malformed_fields)
            _optional_enum(section, "ringingState", _INCOMING_RINGING_STATE_VALUES, malformed_fields)
            _optional_enum(section, "direction", _CALL_DIRECTION_VALUES, malformed_fields)
            _optional_enum(section, "ambiguity", _INCOMING_AMBIGUITY_VALUES, malformed_fields)
        elif section_name == "webRTC":
            for field_name in (
                "hasRemoteAudioElement",
                "remoteAudioAttached",
                "hasRingtoneElement",
            ):
                _optional_bool(section, field_name, malformed_fields)
        elif section_name == "peerConnection":
            for field_name in (
                "hasPeerConnection",
                "hasLocalDescription",
                "hasRemoteDescription",
            ):
                _optional_bool(section, field_name, malformed_fields)
            for field_name in (
                "signalingState",
                "iceConnectionState",
                "connectionState",
            ):
                _optional_nonempty_string(section, field_name, malformed_fields)
            for field_name in ("senderCount", "receiverCount", "transceiverCount"):
                value = section.get(field_name)
                if value is not None and not isinstance(value, int):
                    malformed_fields.append(f"peerConnection.{field_name}")
            _optional_enum(section, "ambiguity", _PEER_CONNECTION_AMBIGUITY_VALUES, malformed_fields)

    if malformed_fields:
        return APNTalkBridgeValidationResult(
            verdict="bridge_malformed",
            bridge_name=contract.bridge_name,
            bridge_version=bridge_version if isinstance(bridge_version, str) else None,
            read_only=read_only if isinstance(read_only, bool) else None,
            mode=mode if isinstance(mode, str) else None,
            sections_present=tuple(sections_present),
            sections_missing=tuple(sections_missing),
            malformed_fields=tuple(malformed_fields),
            why_unavailable="bridge payload does not satisfy the consumer contract",
        )

    if sections_missing:
        return APNTalkBridgeValidationResult(
            verdict="bridge_partial",
            bridge_name=contract.bridge_name,
            bridge_version=bridge_version,
            read_only=read_only,
            mode=mode,
            sections_present=tuple(sections_present),
            sections_missing=tuple(sections_missing),
            malformed_fields=(),
            why_unavailable="bridge payload is present but required sections or fields are missing",
        )

    return APNTalkBridgeValidationResult(
        verdict="bridge_valid",
        bridge_name=contract.bridge_name,
        bridge_version=bridge_version,
        read_only=read_only,
        mode=mode,
        sections_present=tuple(sections_present),
        sections_missing=(),
        malformed_fields=(),
        why_unavailable=None,
    )


APNTALK_SURFACE_CONTRACTS: dict[str, APNTalkSurfaceContract] = {
    "login_agent": APNTalkSurfaceContract(
        tool_name="login_agent",
        selector_name="agent_login_form",
        selector_css="input[type='password']",
        runtime_probe_name="auth_store",
        runtime_probe_path="dom:post_login_authenticated_surface",
    ),
    "wait_for_ready": APNTalkSurfaceContract(
        tool_name="wait_for_ready",
        runtime_probe_name="readiness_snapshot",
        runtime_probe_path="window.__apnTalkTestBridge.readiness",
    ),
    "wait_for_registration": APNTalkSurfaceContract(
        tool_name="wait_for_registration",
        runtime_probe_name="registration_snapshot",
        runtime_probe_path="window.__apnTalkTestBridge.registration",
    ),
    "wait_for_incoming_call": APNTalkSurfaceContract(
        tool_name="wait_for_incoming_call",
        runtime_probe_name="incoming_call_snapshot",
        runtime_probe_path="window.__apnTalkTestBridge.incomingCall",
    ),
    "answer_call": APNTalkSurfaceContract(
        tool_name="answer_call",
        selector_name="answer_call_button",
        selector_css='[data-apntalk-bridge-control-id="softphone-main-answer"]',
        runtime_probe_name="answer_control_snapshot",
        runtime_probe_path="window.__apnTalkTestBridge.controls.answer",
    ),
    "hangup_call": APNTalkSurfaceContract(
        tool_name="hangup_call",
        selector_name="hangup_call_button",
        selector_css='[data-apntalk-bridge-control-id="softphone-main-hangup"]',
        runtime_probe_name="hangup_control_snapshot",
        runtime_probe_path="window.__apnTalkTestBridge.controls.hangup",
    ),
    "get_registration_status": APNTalkSurfaceContract(
        tool_name="get_registration_status",
        runtime_probe_name="registration_snapshot",
        runtime_probe_path="window.__apnTalkTestBridge.registration",
    ),
    "get_store_snapshot": APNTalkSurfaceContract(
        tool_name="get_store_snapshot",
        runtime_probe_name="store_snapshot",
    ),
    "get_peer_connection_summary": APNTalkSurfaceContract(
        tool_name="get_peer_connection_summary",
        runtime_probe_name="peer_connection_summary",
        runtime_probe_path="window.__apnTalkTestBridge.peerConnection",
    ),
}


def get_apntalk_surface_contract(tool_name: str) -> APNTalkSurfaceContract:
    return APNTALK_SURFACE_CONTRACTS[tool_name]


def apntalk_contract_drift_report() -> dict[str, list[str]]:
    return {
        tool_name: contract.missing_requirements()
        for tool_name, contract in APNTALK_SURFACE_CONTRACTS.items()
        if not contract.is_implemented
    }
