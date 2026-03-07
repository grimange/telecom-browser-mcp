from datetime import datetime

from pydantic import BaseModel, Field

from telecom_browser_mcp.models.enums import CallState


class CallSnapshot(BaseModel):
    call_id: str | None = None
    direction: str | None = None
    state: CallState = CallState.IDLE
    ui_state: str | None = None
    store_state: str | None = None
    sip_session_state: str | None = None
    remote_number: str | None = None
    local_number: str | None = None
    started_at: datetime | None = None
    connected_at: datetime | None = None
    ended_at: datetime | None = None
    is_muted: bool | None = None
    is_on_hold: bool | None = None
    correlation_keys: dict[str, str] = Field(default_factory=dict)
    available: bool = True
    reason: str | None = None
