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
    capabilities = None

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
