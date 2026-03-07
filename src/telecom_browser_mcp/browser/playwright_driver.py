from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PlaywrightRuntime:
    playwright: Any = None
    browser: Any = None
    context: Any = None
    page: Any = None


class PlaywrightDriver:
    """Thin wrapper around Playwright with graceful degradation for missing binaries."""

    def __init__(self, headless: bool = True, browser_type: str = "chromium") -> None:
        self.headless = headless
        self.browser_type = browser_type
        self.runtime = PlaywrightRuntime()

    async def open(self, url: str) -> dict[str, str | bool]:
        try:
            from playwright.async_api import async_playwright
        except Exception as exc:  # pragma: no cover - depends on environment
            return {
                "ok": False,
                "message": f"playwright import failed: {exc}",
                "environment_classification": "missing_playwright",
            }

        self.runtime.playwright = await async_playwright().start()
        browser_launcher = getattr(self.runtime.playwright, self.browser_type)
        self.runtime.browser = await browser_launcher.launch(headless=self.headless)
        self.runtime.context = await self.runtime.browser.new_context()
        self.runtime.page = await self.runtime.context.new_page()
        await self.runtime.page.goto(url)
        return {
            "ok": True,
            "message": "browser opened",
            "current_page_url": self.runtime.page.url,
            "page_title": await self.runtime.page.title(),
            "environment_classification": "browser_active",
        }

    async def reset(self, url: str | None = None) -> dict[str, str | bool]:
        page = self.runtime.page
        if page is None:
            return {"ok": False, "message": "no active page"}
        if url:
            await page.goto(url)
        else:
            await page.reload()
        return {"ok": True, "message": "session reset", "current_page_url": page.url}

    async def screenshot(self, path: str) -> bool:
        if self.runtime.page is None:
            return False
        await self.runtime.page.screenshot(path=path)
        return True

    async def close(self) -> None:
        if self.runtime.context is not None:
            await self.runtime.context.close()
        if self.runtime.browser is not None:
            await self.runtime.browser.close()
        if self.runtime.playwright is not None:
            await self.runtime.playwright.stop()
        self.runtime = PlaywrightRuntime()
