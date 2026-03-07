from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from telecom_browser_mcp.browser.diagnostics import BrowserDiagnosticsCollector


@dataclass(slots=True)
class PlaywrightRuntime:
    playwright: Any = None
    browser: Any = None
    context: Any = None
    page: Any = None
    diagnostics: BrowserDiagnosticsCollector | None = None


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
        self.runtime.diagnostics = BrowserDiagnosticsCollector(trace_enabled=True)
        await self.runtime.diagnostics.attach(
            context=self.runtime.context,
            page=self.runtime.page,
        )
        self.runtime.diagnostics.mark("goto_started")
        await self.runtime.page.goto(url)
        self.runtime.diagnostics.mark("goto_completed")
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

    async def collect_diagnostics_bundle(
        self,
        *,
        base_dir: str,
        run_id: str,
        scenario_id: str,
        session_id: str,
        fault_type: str,
        injection_point: str,
        status: str,
        failure_classification: str,
        attempted_selector: str | None = None,
    ) -> dict[str, Any]:
        collector = self.runtime.diagnostics or BrowserDiagnosticsCollector(trace_enabled=False)
        self.runtime.diagnostics = collector
        return await collector.write_bundle(
            base_dir=base_dir,
            run_id=run_id,
            scenario_id=scenario_id,
            session_id=session_id,
            fault_type=fault_type,
            injection_point=injection_point,
            status=status,
            failure_classification=failure_classification,
            attempted_selector=attempted_selector,
        )

    async def close(self) -> None:
        if self.runtime.context is not None:
            await self.runtime.context.close()
        if self.runtime.browser is not None:
            await self.runtime.browser.close()
        if self.runtime.playwright is not None:
            await self.runtime.playwright.stop()
        self.runtime = PlaywrightRuntime()
