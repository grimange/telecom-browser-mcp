from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AdapterCapabilities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supports_login: bool = False
    supports_registration_detection: bool = False
    supports_incoming_call_detection: bool = False
    supports_answer_action: bool = False
    supports_hangup_action: bool = False
    supports_webrtc_summary: bool = False


class TelecomStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    browser_open: bool = False
    adapter_attached: bool = False
    login_complete: bool = False
    ui_ready: bool = False
    registration_state: str = "unknown"
    incoming_call_state: str = "unknown"
    active_call_state: str = "unknown"


class SessionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    adapter_id: str
    adapter_version: str = "0.1"
    capabilities: AdapterCapabilities = Field(default_factory=AdapterCapabilities)
    target_url: str
    lifecycle_state: str = "starting"
    artifact_root: str
    browser_launch_error: str | None = None
    browser_launch_error_classification: str | None = None
    telecom: TelecomStatus = Field(default_factory=TelecomStatus)


class SessionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    adapter_id: str
    lifecycle_state: str
    target_url: str
    registration_state: str
    incoming_call_state: str
    active_call_state: str
