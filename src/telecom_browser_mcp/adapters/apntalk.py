from __future__ import annotations

from typing import Any

from telecom_browser_mcp.adapters.apntalk_contract import (
    APNTALK_CONTRACT_VERSION,
    get_apntalk_surface_contract,
)
from telecom_browser_mcp.adapters.base import AdapterBase, AdapterOperationResult
from telecom_browser_mcp.models.session import AdapterCapabilities, TelecomStatus


class APNTalkAdapter(AdapterBase):
    adapter_id = "apntalk"
    adapter_name = "APNTalk"
    adapter_version = "0.1"
    contract_version = APNTALK_CONTRACT_VERSION
    scenario_id = "apntalk-modernization-baseline"
    support_status = "contract_scaffold_only"
    capabilities = AdapterCapabilities(
        supports_login=False,
        supports_registration_detection=False,
        supports_incoming_call_detection=False,
        supports_answer_action=False,
        supports_hangup_action=False,
        supports_webrtc_summary=True,
    )

    async def wait_for_ready(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("wait_for_ready")
        return self._failure(
            "APNTalk selector contract is not implemented; refusing scaffold ready-state success",
            error_code="selector_contract_missing",
            classification="ui_drift",
            missing_requirements=contract.missing_requirements(),
        )

    async def login(
        self,
        status: TelecomStatus,
        page: Any,
        credentials: dict[str, Any],
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, credentials, timeout_ms)
        contract = get_apntalk_surface_contract("login_agent")
        return self._failure(
            "APNTalk login contract is not implemented",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def wait_for_registration(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("wait_for_registration")
        return self._failure(
            "APNTalk registration runtime probe is not implemented",
            error_code="runtime_probe_unavailable",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def wait_for_incoming_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("wait_for_incoming_call")
        return self._failure(
            "APNTalk incoming-call runtime probe is not implemented",
            error_code="runtime_probe_unavailable",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def answer_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("answer_call")
        return self._failure(
            "APNTalk answer action contract is not implemented",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def hangup_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        contract = get_apntalk_surface_contract("hangup_call")
        return self._failure(
            "APNTalk hangup action contract is not implemented",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
            missing_requirements=contract.missing_requirements(),
        )

    async def registration_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        contract = get_apntalk_surface_contract("get_registration_status")
        return {
            "available": False,
            "registration_state": status.registration_state,
            "reason": "APNTalk registration snapshot probe is not implemented",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "missing_requirements": contract.missing_requirements(),
        }

    async def store_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        contract = get_apntalk_surface_contract("get_store_snapshot")
        return {
            "available": False,
            "reason": "APNTalk store snapshot probe is not implemented",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "missing_requirements": contract.missing_requirements(),
        }

    async def peer_connection_summary(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        contract = get_apntalk_surface_contract("get_peer_connection_summary")
        return {
            "available": False,
            "reason": "APNTalk runtime object path not configured; add verified inspector path in adapter hardening",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "missing_requirements": contract.missing_requirements(),
        }
