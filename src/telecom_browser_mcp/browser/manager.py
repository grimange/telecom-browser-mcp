from __future__ import annotations

from dataclasses import dataclass

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright


@dataclass
class BrowserHandle:
    browser_open: bool
    launch_error: str | None = None
    launch_error_classification: str | None = None
    target_url: str | None = None
    playwright: Playwright | None = None
    browser: Browser | None = None
    context: BrowserContext | None = None
    page: Page | None = None


class BrowserManager:
    async def open(self, target_url: str, headless: bool = True) -> BrowserHandle:
        handle = BrowserHandle(browser_open=False, target_url=target_url)
        playwright: Playwright | None = None
        browser: Browser | None = None
        context: BrowserContext | None = None
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)

            handle.playwright = playwright
            handle.browser = browser
            handle.context = context
            handle.page = page
            handle.browser_open = True
            return handle
        except Exception as exc:  # pragma: no cover - environment dependent
            message = str(exc)
            classification = "unknown"
            lowered = message.lower()
            if "executable doesn't exist" in lowered or "browser" in lowered and "install" in lowered:
                classification = "environment_limit_missing_browser_binary"
            elif "permission" in lowered or "sandbox" in lowered:
                classification = "permission_blocked"
            elif "net::" in lowered or "timed out" in lowered:
                classification = "environment_limit_unreachable_target"
            handle.launch_error = message
            handle.launch_error_classification = classification
            if context is not None:
                await context.close()
            if browser is not None:
                await browser.close()
            if playwright is not None:
                await playwright.stop()
            return handle

    async def close(self, handle: BrowserHandle) -> None:
        if handle.context is not None:
            await handle.context.close()
        if handle.browser is not None:
            await handle.browser.close()
        if handle.playwright is not None:
            await handle.playwright.stop()
        handle.browser_open = False
