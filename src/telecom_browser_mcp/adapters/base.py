from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any

from telecom_browser_mcp.models.session import TelecomStatus


@dataclass(frozen=True)
class AdapterOperationResult:
    ok: bool
    message: str
    error_code: str | None = None
    classification: str = "unknown"
    retryable: bool = False
    details: dict[str, Any] = field(default_factory=dict)


class AdapterBase(ABC):
    adapter_id = "base"
    adapter_name = "base"
    adapter_version = "0.1"
    contract_version = "v1"
    scenario_id = "baseline"
    support_status = "supported"
    capabilities = None

    def capability_truth(self, observation: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        _ = observation
        capability_map = {
            "login_agent": bool(getattr(self.capabilities, "supports_login", False)),
            "wait_for_registration": bool(
                getattr(self.capabilities, "supports_registration_detection", False)
            ),
            "wait_for_incoming_call": bool(
                getattr(self.capabilities, "supports_incoming_call_detection", False)
            ),
            "answer_call": bool(getattr(self.capabilities, "supports_answer_action", False)),
            "hangup_call": bool(getattr(self.capabilities, "supports_hangup_action", False)),
            "get_peer_connection_summary": bool(
                getattr(self.capabilities, "supports_webrtc_summary", False)
            ),
        }
        truths: list[dict[str, Any]] = []
        for capability, enabled in capability_map.items():
            truths.append(
                {
                    "capability": capability,
                    "declared_support": "supported" if enabled else "unsupported_by_design",
                    "binding_status": "bound" if enabled else "unbound",
                    "live_detection_status": "not_checked",
                    "why_unavailable": None if enabled else "adapter capability flag is false",
                }
            )
        return truths

    async def phase0_observation(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        return {
            "adapter_id": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "support_status": self.support_status,
            "capability_truth": self.capability_truth(),
        }

    def _success(self, message: str, **details: Any) -> AdapterOperationResult:
        return AdapterOperationResult(ok=True, message=message, details=details)

    def _failure(
        self,
        message: str,
        *,
        error_code: str,
        classification: str,
        retryable: bool = False,
        **details: Any,
    ) -> AdapterOperationResult:
        return AdapterOperationResult(
            ok=False,
            message=message,
            error_code=error_code,
            classification=classification,
            retryable=retryable,
            details=details,
        )

    async def login(
        self,
        status: TelecomStatus,
        page: Any,
        credentials: dict[str, Any],
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, credentials, timeout_ms)
        return self._failure(
            "login unsupported",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
        )

    async def wait_for_ready(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (page, timeout_ms)
        status.ui_ready = True
        return self._success("ready")

    async def wait_for_registration(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        return self._failure(
            "registration unsupported",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
        )

    async def wait_for_incoming_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        return self._failure(
            "incoming call detection unsupported",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
        )

    async def answer_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        return self._failure(
            "answer unsupported",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
        )

    async def hangup_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = (status, page, timeout_ms)
        return self._failure(
            "hangup unsupported",
            error_code="adapter_contract_unimplemented",
            classification="adapter_contract_failure",
        )

    async def registration_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = page
        return {
            "available": status.registration_state != "unknown",
            "registration_state": status.registration_state,
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }

    async def store_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        return {
            "available": False,
            "reason": "adapter does not expose store snapshot",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }

    async def peer_connection_summary(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        return {
            "available": False,
            "reason": "adapter does not expose webrtc summary",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
