from datetime import datetime, timezone

from pydantic import BaseModel, Field

from telecom_browser_mcp.models.enums import RegistrationState


class RegistrationSnapshot(BaseModel):
    state: RegistrationState = RegistrationState.UNKNOWN
    ui_badge_state: str | None = None
    sip_stack_state: str | None = None
    ws_connected: bool | None = None
    registered: bool = False
    last_error: str | None = None
    source_confidence: float = 0.0
    available: bool = True
    reason: str | None = None
    source: str = "adapter"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
