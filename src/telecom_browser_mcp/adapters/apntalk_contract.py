from __future__ import annotations

from dataclasses import dataclass


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

APNTALK_SURFACE_CONTRACTS: dict[str, APNTalkSurfaceContract] = {
    "login_agent": APNTalkSurfaceContract(
        tool_name="login_agent",
        selector_name="agent_login_form",
        runtime_probe_name="auth_store",
    ),
    "wait_for_ready": APNTalkSurfaceContract(
        tool_name="wait_for_ready",
        selector_name="agent_ready_indicator",
    ),
    "wait_for_registration": APNTalkSurfaceContract(
        tool_name="wait_for_registration",
        selector_name="registration_badge",
        runtime_probe_name="registration_snapshot",
    ),
    "wait_for_incoming_call": APNTalkSurfaceContract(
        tool_name="wait_for_incoming_call",
        selector_name="incoming_call_banner",
        runtime_probe_name="incoming_call_snapshot",
    ),
    "answer_call": APNTalkSurfaceContract(
        tool_name="answer_call",
        selector_name="answer_call_button",
        runtime_probe_name="active_call_snapshot",
    ),
    "hangup_call": APNTalkSurfaceContract(
        tool_name="hangup_call",
        selector_name="hangup_call_button",
        runtime_probe_name="active_call_snapshot",
    ),
    "get_registration_status": APNTalkSurfaceContract(
        tool_name="get_registration_status",
        selector_name="registration_badge",
        runtime_probe_name="registration_snapshot",
    ),
    "get_store_snapshot": APNTalkSurfaceContract(
        tool_name="get_store_snapshot",
        runtime_probe_name="store_snapshot",
    ),
    "get_peer_connection_summary": APNTalkSurfaceContract(
        tool_name="get_peer_connection_summary",
        runtime_probe_name="peer_connection_summary",
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
