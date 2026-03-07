from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from telecom_browser_mcp.browser.playwright_driver import PlaywrightDriver
from telecom_browser_mcp.models.enums import BrowserSessionState


@dataclass
class BrowserSession:
    session_id: str
    run_id: str
    adapter_name: str
    adapter_version: str
    artifacts_dir: str
    headless: bool
    browser_type: str = "chromium"
    base_url: str | None = None
    origin: str | None = None
    status: BrowserSessionState = BrowserSessionState.ACTIVE
    environment_classification: str = "unknown"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    current_page_url: str | None = None
    page_title: str | None = None
    driver: PlaywrightDriver | None = None

    def touch(self) -> None:
        self.last_activity_at = datetime.now(timezone.utc)

    def ensure_driver(self) -> PlaywrightDriver:
        if self.driver is None:
            self.driver = PlaywrightDriver(headless=self.headless, browser_type=self.browser_type)
        return self.driver
