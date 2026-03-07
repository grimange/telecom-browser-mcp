from datetime import datetime, timezone

from pydantic import BaseModel, Field

from telecom_browser_mcp.models.enums import BrowserSessionState


class BrowserSessionModel(BaseModel):
    session_id: str
    run_id: str
    status: BrowserSessionState = BrowserSessionState.ACTIVE
    adapter_name: str
    adapter_version: str
    base_url: str | None = None
    origin: str | None = None
    headless: bool = True
    browser_type: str = "chromium"
    environment_classification: str = "unknown"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_page_url: str | None = None
    page_title: str | None = None
    artifacts_dir: str
